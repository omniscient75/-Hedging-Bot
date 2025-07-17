import os
import requests

def send_telegram_alert(message):
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        resp = requests.post(url, data=data, timeout=5)
        return resp.status_code == 200
    except Exception as e:
        from loguru import logger
        logger.error(f"Failed to send Telegram alert: {e}")
        return False 