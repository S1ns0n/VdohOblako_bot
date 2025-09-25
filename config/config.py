import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    YANDEX_API_TOKEN = os.environ.get('YANDEX_API_TOKEN')
    YANDEX_MAIN_PATH = os.environ.get('YANDEX_MAIN_PATH')
