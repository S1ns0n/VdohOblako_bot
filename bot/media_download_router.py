from aiogram import Bot, types, F
from aiogram import Router
import asyncio
from aiogram import F, types
from aiogram.filters import Filter
from aiogram.filters import Command

from yandex_api.yandex_api import YandexManager
from .keyboards import Keyboards
from .utils import Utils
from config.config import Config
from .disk_manager_router import manager



media_downloader = Router()
media_groups = {}

@media_downloader.message(F.photo & ~F.media_group_id)
async def download_single_photo(message: types.Message, bot: Bot):
    """Обработка одиночных фото"""
    try:
        print(manager.current_path)
        photo = message.photo[-1]
        photo_io = await bot.download(photo.file_id)

        await manager.upload_file(file_obj=photo_io, filename=photo.file_id)
        await message.answer("Загружено!")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


# Обработчик медиагрупп (часть альбома)
@media_downloader.message(F.photo & F.media_group_id)
async def handle_media_group(message: types.Message, bot: Bot):
    """Обработка медиагрупп (альбомов)"""
    media_group_id = message.media_group_id

    # Если это первое медиа в группе
    if media_group_id not in media_groups:
        media_groups[media_group_id] = {
            'messages': [],
            'processed': False,
            'chat_id': message.chat.id
        }

        # Устанавливаем таймер для обработки всей группы
        asyncio.create_task(process_media_group(media_group_id=media_group_id,
                                                bot=bot,
                                                message_id=message.message_id))

    # Добавляем сообщение в группу
    media_groups[media_group_id]['messages'].append(message)


async def process_media_group(media_group_id: str, bot: Bot, message_id: int):
    """Обработка всей медиагруппы после небольшой задержки"""
    # Ждем 3 секунды, чтобы все медиа группы успели прийти
    await asyncio.sleep(3)

    if media_group_id not in media_groups:
        return

    group_data = media_groups[media_group_id]

    # Если группа уже обработана или пуста - выходим
    if group_data['processed'] or not group_data['messages']:
        return

    group_data['processed'] = True
    messages = group_data['messages']
    chat_id = group_data['chat_id']

    try:
        downloaded_files = []

        # Скачиваем все медиа из группы
        for msg in messages:
            if msg.photo:
                photo = msg.photo[-1]
                photo_io = await bot.download(photo.file_id)
                await manager.upload_file(file_obj=photo_io, filename=photo.file_id)
                downloaded_files.append(photo.file_id)

        # Отправляем итоговое сообщение
        await bot.send_message(chat_id=chat_id,
                               text=f"✅ Медиагруппа загружена! Файлов: {len(downloaded_files)}",
                               reply_to_message_id=message_id)

    except Exception as e:
        error_message = f"❌ Ошибка загрузки медиагруппы: {str(e)}"
        await bot.send_message(chat_id, error_message)

    finally:
        # Удаляем обработанную группу из временного хранилища
        if media_group_id in media_groups:
            del media_groups[media_group_id]