from aiogram import Bot, types, F
from aiogram import Router
from aiogram.filters import Command

from yandex_api.yandex_api import YandexManager
from .keyboards import Keyboards
from .utils import Utils
from config.config import Config
from .disk_manager_router import manager



media_downloader = Router()


@media_downloader.message(F.photo)
async def download_photo(message: types.Message, bot: Bot):
    try:
        print(manager.current_path)
        photo = message.photo[-1]
        photo_io = await bot.download(photo.file_id)

        await manager.upload_file(file_obj=photo_io, filename=photo.file_id)

        await message.answer("загружено!")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
