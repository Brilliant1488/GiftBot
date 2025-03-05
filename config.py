# config.py
from aiogram import Bot, Dispatcher

API_TOKEN = "7845726866:AAHgktaRK9JdtMeJjFrbGceFeZCOAYBnspI"
OWNER_ID = "8030736166"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

COMMON_AMOUNTS = [5, 15, 25, 50, 100, 150, 200, 350, 500, 1000]
WELCOME_IMAGE_URL = "https://i.postimg.cc/LXkpFV8H/photo-2025-01-27-11-29-49.jpg"
INSTRUCTIONS_PATH = r"C:\Users\Brilliant\PycharmProjects\BotShop\instructions"

USDT_WALLET_ADDRESS = "T123abc456def789ghi"  # Пример адреса USDT TRC20
CARD_DETAILS = """
Банк: YourBankName
Номер карты: 1234 5678 9012 3456
Получатель: Иван Иванов
"""