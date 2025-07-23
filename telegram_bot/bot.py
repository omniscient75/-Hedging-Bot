import asyncio
import nest_asyncio
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters)
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, REGISTRATION_MODE, ADMIN_USER_IDS, INVITE_CODE, TELEGRAM_ALLOWED_USER_IDS
from logger import logger

# Enable nested event loops for Python 3.13 compatibility
nest_asyncio.apply()

# User session store (simple in-memory for demo)
user_sessions: Dict[int, Dict[str, Any]] = {}

# Risk manager will be injected
risk_manager = None

# --- Authentication ---
def is_authenticated(user_id: int) -> bool:
    return str(user_id) in TELEGRAM_ALLOWED_USER_IDS or str(user_id) in ADMIN_USER_IDS

# --- Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id in ADMIN_USER_IDS:
        await update.message.reply_text("Welcome, Admin! You have full access.")
        return
    if is_authenticated(user_id):
        await update.message.reply_text("Welcome back!")
        return
    if REGISTRATION_MODE == 'admin':
        # Notify all admins for approval
        for admin_id in ADMIN_USER_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"User {user_id} ({update.effective_user.full_name}) requests access. Approve with /approve {user_id}"
                )
            except Exception as e:
                logger.error(f"Failed to notify admin {admin_id}: {e}")
        await update.message.reply_text("Your registration request has been sent to the admin. Please wait for approval.")
    elif REGISTRATION_MODE == 'open':
        TELEGRAM_ALLOWED_USER_IDS.add(user_id)
        await update.message.reply_text("You have been registered and can now use the bot!")
        # Notify all admins about the new user
        for admin_id in ADMIN_USER_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"New user registered: {update.effective_user.full_name} (ID: {user_id})"
                )
            except Exception as e:
                logger.error(f"Failed to notify admin {admin_id}: {e}")
    elif REGISTRATION_MODE == 'invite':
        await update.message.reply_text("Please enter the invite code to register:")
        context.user_data['awaiting_invite_code'] = True
    else:
        await update.message.reply_text("Registration mode is not configured correctly.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authenticated(user_id):
        await update.message.reply_text("Unauthorized user.")
        return
    help_text = (
        "/monitor_risk - View real-time risk metrics\n"
        "/hedge_status - View current hedge status\n"
        "/auto_hedge - Toggle auto-hedging\n"
    )
    await update.message.reply_text(help_text)

async def monitor_risk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authenticated(user_id):
        await update.message.reply_text("Unauthorized user.")
        return
    
    if risk_manager:
        # Get real risk data
        risk_message = risk_manager.get_formatted_risk_message()
        positions_message = risk_manager.get_formatted_positions_message()
        full_message = f"{risk_message}\n\n{positions_message}"
    else:
        full_message = "Risk manager not available."
    
    msg = await update.message.reply_text(
        full_message,
        reply_markup=main_keyboard()
    )
    # Store message id for editing
    user_sessions[user_id]["risk_msg_id"] = msg.message_id

async def hedge_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authenticated(user_id):
        await update.message.reply_text("Unauthorized user.")
        return
    
    if risk_manager and risk_manager.last_risk_update:
        risk = risk_manager.last_risk_update
        status = "🟢 Neutral" if abs(risk.total_delta) < 0.1 else "🟡 Hedging needed" if abs(risk.total_delta) < 0.5 else "🔴 High risk"
        message = f"Hedge Status: {status}\nTotal Delta: {risk.total_delta:.4f}\nVaR: ${risk.portfolio_var:.2f}"
    else:
        message = "Hedge Status: No data available."
    
    await update.message.reply_text(
        message,
        reply_markup=main_keyboard()
    )

async def auto_hedge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authenticated(user_id):
        await update.message.reply_text("Unauthorized user.")
        return
    # Toggle auto-hedge (demo)
    session = user_sessions.setdefault(user_id, {})
    auto = session.get("auto_hedge", False)
    session["auto_hedge"] = not auto
    await update.message.reply_text(
        f"Auto-hedge is now {'ON' if not auto else 'OFF'}.",
        reply_markup=main_keyboard()
    )

# --- Interactive Buttons ---
def main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Hedge Now", callback_data="hedge_now"),
            InlineKeyboardButton("Adjust Threshold", callback_data="adjust_threshold"),
        ],
        [
            InlineKeyboardButton("View Analytics", callback_data="view_analytics"),
        ]
    ])

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_authenticated(user_id):
        await query.answer("Unauthorized.", show_alert=True)
        return
    await query.answer()
    if query.data == "hedge_now":
        await query.edit_message_text("Hedging now... (demo)", reply_markup=main_keyboard())
        logger.info(f"User {user_id} triggered Hedge Now.")
    elif query.data == "adjust_threshold":
        await query.edit_message_text("Adjust threshold feature coming soon.", reply_markup=main_keyboard())
    elif query.data == "view_analytics":
        await query.edit_message_text("Analytics: (demo)\nPnL: 0.00\nSharpe: 0.00", reply_markup=main_keyboard())

# --- Registration Handler ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if context.user_data.get('awaiting_invite_code'):
        code = update.message.text.strip()
        if code == INVITE_CODE:
            TELEGRAM_ALLOWED_USER_IDS.add(user_id)
            context.user_data['awaiting_invite_code'] = False
            await update.message.reply_text("Invite code accepted! You are now registered.")
        else:
            await update.message.reply_text("Incorrect invite code. Please try again:")
    else:
        await update.message.reply_text("Unknown command or message.")

# --- Approve Command ---
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = str(update.effective_user.id)
    if admin_id not in ADMIN_USER_IDS:
        await update.message.reply_text("You are not authorized to approve users.")
        return
    if context.args and len(context.args) == 1:
        approve_id = context.args[0]
        TELEGRAM_ALLOWED_USER_IDS.add(approve_id)
        await update.message.reply_text(f"User {approve_id} has been approved.")
        try:
            await context.bot.send_message(chat_id=approve_id, text="Your registration has been approved! You can now use the bot.")
        except Exception:
            pass
    else:
        await update.message.reply_text("Usage: /approve <user_id>")

# --- Error Handler ---
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Bot error: {context.error}")
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text("An error occurred. Please try again later.")

# --- Bot Initialization ---
def run_bot(risk_mgr=None):
    global risk_manager
    risk_manager = risk_mgr
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("monitor_risk", monitor_risk))
    app.add_handler(CommandHandler("hedge_status", hedge_status))
    app.add_handler(CommandHandler("auto_hedge", auto_hedge))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    logger.info("Telegram bot started.")
    app.run_polling()

if __name__ == "__main__":
    run_bot() 