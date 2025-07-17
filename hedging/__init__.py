from .strategies import HedgingStrategy
# from .execution import SmartOrderRouter, ExecutionMode 
import time
from loguru import logger
import requests

def log_performance(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"{func.__name__} executed in {duration:.2f}s")
        return result
    return wrapper 

def health_check():
    try:
        # Check DB, API, etc.
        logger.info("Health check passed.")
    except Exception as e:
        logger.critical(f"Health check failed: {e}")
        # Send alert (e.g., via Telegram)

async def handle_telegram_command(bot, chat_id):
    try:
        # Bot command logic
        pass
    except Exception as e:
        logger.error(f"Telegram command error: {e}", exc_info=True)
        await bot.send_message(chat_id, "Sorry, something went wrong. Please try again later.")

def make_api_request(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}", exc_info=True)
        # Optionally, implement retry or fallback here

logger.info(f"Order placed: {order_id} for {symbol} at {price}")
logger.warning(f"High latency detected: {latency}s for {endpoint}")
logger.error(f"Order failed: {order_id} - {error_message}")

import time

def retry_api_call(api_func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return api_func()
        except Exception as e:
            logger.warning(f"API call failed (attempt {attempt+1}): {e}")
            time.sleep(2 ** attempt)
    logger.error("API call failed after retries.")
    raise