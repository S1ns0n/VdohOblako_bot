from aiogram import Bot, types, F
from aiogram import Router
from aiogram.filters import Command

from yandex_api.yandex_api import YandexManager
from .keyboards import Keyboards
from .utils import Utils
from config.config import Config


from database.database import (
    create_user,
    get_all_users,
    get_user_by_tg_id,
    delete_user,
    get_user_count
)


registration_router = Router()
keyboards = Keyboards()


@registration_router.message(Command('start'))
async def start_bot(message: types.Message, bot: Bot):


    loading_msg = await bot.send_message(message.from_user.id, "⏳ Загрузка...")

    await create_user(tg_id=message.from_user.id)

    await loading_msg.edit_text(
        text=f"Вы зареганы!")
