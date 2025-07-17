import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from loguru import logger
import uuid

class ExecutionStatus:
    PENDING = 'pending'
    SUBMITTED = 'submitted'
    PARTIALLY_FILLED = 'partially_filled'
    FILLED = 'filled'
    CANCELLED = 'cancelled'
    FAILED = 'failed'

class ExecutionAuditRecord:
    def __init__(self, execution_id: str, timestamp: datetime, action: str, details: Dict):
        self.execution_id = execution_id
        self.timestamp = timestamp
        self.action = action
        self.details = details

class ExecutionAuditTrail:
    def __init__(self):
        self.records: List[ExecutionAuditRecord] = []
    def log(self, execution_id: str, action: str, details: Dict):
        record = ExecutionAuditRecord(execution_id, datetime.now(), action, details)
        self.records.append(record)
        logger.info(f"[AUDIT] {execution_id} | {action} | {details}")
    def get_records(self, execution_id: Optional[str] = None) -> List[ExecutionAuditRecord]:
        if execution_id:
            return [r for r in self.records if r.execution_id == execution_id]
        return self.records

class ExecutionManager:
    """Manages hedge execution, order routing, and audit trails"""
    def __init__(self, exchange_manager, risk_manager):
        self.exchange_manager = exchange_manager
        self.risk_manager = risk_manager
        self.audit_trail = ExecutionAuditTrail()
        self.active_executions: Dict[str, Dict] = {}

    async def execute_hedge(self, symbol: str, target_delta: float, max_slippage: float = 0.002, partial: bool = True, twap: bool = True) -> Dict:
        """
        Execute optimal hedge for a symbol to reach target delta.
        Returns execution summary with cost-benefit analysis and audit trail.
        """
        execution_id = str(uuid.uuid4())
        self.audit_trail.log(execution_id, 'start_execution', {'symbol': symbol, 'target_delta': target_delta})
        
        # 1. Calculate optimal hedge size
        hedge_size, rationale = await self._calculate_optimal_hedge_size(symbol, target_delta)
        self.audit_trail.log(execution_id, 'hedge_size_calculated', {'hedge_size': hedge_size, 'rationale': rationale})
        
        # 2. Smart order routing
        venue, order_params, routing_reason = await self._route_order(symbol, hedge_size, max_slippage)
        self.audit_trail.log(execution_id, 'order_routed', {'venue': venue, 'order_params': order_params, 'reason': routing_reason})
        
        # 3. Partial hedging / gradual adjustment
        tranches = self._split_into_tranches(hedge_size, partial, twap)
        self.audit_trail.log(execution_id, 'tranches_created', {'tranches': tranches})
        
        # 4. Market impact minimization (TWAP/VWAP/randomization)
        execution_results = []
        for i, tranche in enumerate(tranches):
            tranche_id = f"{execution_id}_tranche_{i+1}"
            self.audit_trail.log(tranche_id, 'tranche_execution_start', {'size': tranche, 'venue': venue})
            result = await self._execute_tranche(symbol, tranche, venue, order_params, max_slippage, twap, tranche_id)
            execution_results.append(result)
            self.audit_trail.log(tranche_id, 'tranche_execution_result', result)
        
        # 5. Execution confirmation & status tracking
        status = self._aggregate_status(execution_results)
        self.audit_trail.log(execution_id, 'execution_status', {'status': status})
        
        # 6. Cost-benefit analysis
        cost_benefit = self._cost_benefit_analysis(execution_results, hedge_size, target_delta)
        self.audit_trail.log(execution_id, 'cost_benefit', cost_benefit)
        
        # 7. Final summary
        summary = {
            'execution_id': execution_id,
            'symbol': symbol,
            'target_delta': target_delta,
            'hedge_size': hedge_size,
            'venue': venue,
            'status': status,
            'execution_results': execution_results,
            'cost_benefit': cost_benefit,
            'audit_trail': [r.__dict__ for r in self.audit_trail.get_records(execution_id)]
        }
        self.active_executions[execution_id] = summary
        self.audit_trail.log(execution_id, 'execution_complete', {'summary': summary})
        return summary

    async def _calculate_optimal_hedge_size(self, symbol: str, target_delta: float) -> Tuple[float, str]:
        """Calculate optimal hedge size based on risk, liquidity, volatility, and slippage."""
        # Get current position and risk
        position = await self.risk_manager.get_position(symbol)
        current_delta = position.get('delta', 0)
        market_data = await self.exchange_manager.get_market_data(symbol)
        volatility = market_data.get('volatility', 0.05)
        liquidity = market_data.get('order_book_liquidity', 100000)
        max_hedge = liquidity * 0.1  # Don't exceed 10% of book
        # Adjust for volatility: smaller size in high vol
        vol_factor = max(0.5, 1 - volatility)
        raw_hedge = target_delta - current_delta
        hedge_size = max(-max_hedge, min(max_hedge, raw_hedge * vol_factor))
        rationale = f"Current delta: {current_delta}, Target: {target_delta}, Vol: {volatility}, Liquidity: {liquidity}, Max hedge: {max_hedge}, Vol factor: {vol_factor}"
        return hedge_size, rationale

    async def _route_order(self, symbol: str, hedge_size: float, max_slippage: float) -> Tuple[str, Dict, str]:
        """Route order to best venue based on price, depth, fees, and latency."""
        venues = await self.exchange_manager.get_available_venues(symbol)
        best_venue = None
        best_score = float('-inf')
        best_params = {}
        reason = ""
        for venue in venues:
            order_book = await self.exchange_manager.get_order_book(symbol, venue)
            price = order_book.get('best_ask' if hedge_size > 0 else 'best_bid', 0)
            depth = order_book.get('depth', 0)
            fees = order_book.get('fees', 0.0004)
            latency = order_book.get('latency', 0.1)
            score = -abs(price) - fees * 1000 - latency * 10 + depth * 0.01
            if score > best_score:
                best_score = score
                best_venue = venue
                best_params = {'price': price, 'depth': depth, 'fees': fees, 'latency': latency}
        reason = f"Best venue: {best_venue}, Score: {best_score}, Params: {best_params}"
        return best_venue, best_params, reason

    def _split_into_tranches(self, hedge_size: float, partial: bool, twap: bool) -> List[float]:
        """Split hedge into tranches for partial/gradual execution."""
        if not partial or abs(hedge_size) < 1:
            return [hedge_size]
        n_tranches = min(5, max(2, int(abs(hedge_size) // 1))) if twap else 2
        tranche_size = hedge_size / n_tranches
        return [tranche_size] * n_tranches

    async def _execute_tranche(self, symbol: str, tranche: float, venue: str, order_params: Dict, max_slippage: float, twap: bool, tranche_id: str) -> Dict:
        """Execute a single tranche, with market impact minimization."""
        # Simulate TWAP delay
        if twap:
            await asyncio.sleep(1)
        # Place order
        try:
            order_result = await self.exchange_manager.place_order(
                symbol=symbol,
                venue=venue,
                side='buy' if tranche > 0 else 'sell',
                quantity=abs(tranche),
                price=order_params['price'],
                max_slippage=max_slippage
            )
            status = ExecutionStatus.FILLED if order_result.get('filled', 0) == abs(tranche) else ExecutionStatus.PARTIALLY_FILLED
            cost = order_result.get('cost', 0)
            slippage = order_result.get('slippage', 0)
            fees = order_result.get('fees', 0)
            return {
                'tranche_id': tranche_id,
                'status': status,
                'filled': order_result.get('filled', 0),
                'cost': cost,
                'slippage': slippage,
                'fees': fees,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Execution error for {tranche_id}: {e}")
            return {
                'tranche_id': tranche_id,
                'status': ExecutionStatus.FAILED,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _aggregate_status(self, execution_results: List[Dict]) -> str:
        statuses = [r['status'] for r in execution_results]
        if all(s == ExecutionStatus.FILLED for s in statuses):
            return ExecutionStatus.FILLED
        if any(s == ExecutionStatus.FAILED for s in statuses):
            return ExecutionStatus.FAILED
        if any(s == ExecutionStatus.PARTIALLY_FILLED for s in statuses):
            return ExecutionStatus.PARTIALLY_FILLED
        return ExecutionStatus.PENDING

    def _cost_benefit_analysis(self, execution_results: List[Dict], hedge_size: float, target_delta: float) -> Dict:
        total_cost = sum(r.get('cost', 0) for r in execution_results)
        total_fees = sum(r.get('fees', 0) for r in execution_results)
        total_slippage = sum(r.get('slippage', 0) for r in execution_results)
        filled = sum(r.get('filled', 0) for r in execution_results)
        effective_delta = filled
        benefit = abs(effective_delta) / abs(target_delta) if target_delta else 0
        return {
            'total_cost': total_cost,
            'total_fees': total_fees,
            'total_slippage': total_slippage,
            'filled': filled,
            'target_delta': target_delta,
            'benefit': benefit,
            'cost_per_unit': total_cost / filled if filled else 0
        }

    def get_audit_trail(self, execution_id: str) -> List[Dict]:
        return [r.__dict__ for r in self.audit_trail.get_records(execution_id)]

    def get_active_executions(self) -> Dict[str, Dict]:
        return self.active_executions 