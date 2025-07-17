import os
from dotenv import load_dotenv

load_dotenv()

# Exchange API Keys
BYBIT_API_KEY = os.getenv('BYBIT_API_KEY')
BYBIT_API_SECRET = os.getenv('BYBIT_API_SECRET')

# Telegram Bot
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# General Settings
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Risk Parameters
MAX_DELTA = float(os.getenv('MAX_DELTA', '1.0'))
MAX_GAMMA = float(os.getenv('MAX_GAMMA', '1.0'))
MAX_VEGA = float(os.getenv('MAX_VEGA', '1.0'))
MAX_THETA = float(os.getenv('MAX_THETA', '1.0'))
