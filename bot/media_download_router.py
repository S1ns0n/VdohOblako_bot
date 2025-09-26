import asyncio

from aiogram import Bot
from aiogram import F, types
from aiogram import Router

from .disk_manager_router import session_manager
from logger import main_logger
media_downloader = Router()
media_groups = {}


@media_downloader.message(F.photo & ~F.media_group_id)
async def download_single_photo(message: types.Message, bot: Bot):
    """Обработка одиночных фото с использованием сессии пользователя"""
    try:
        user_session = await session_manager.get_user_session(message.from_user.id)
        photo = message.photo[-1]
        photo_io = await bot.download(photo.file_id)

        # Получаем информацию о файле
        file_info = await bot.get_file(photo.file_id)

        # Используем оригинальное имя файла или генерируем свое
        if hasattr(file_info, 'file_path') and file_info.file_path:
            original_filename = file_info.file_path.split('/')[-1]
            # Убираем префиксы телеграма если они есть
            if original_filename.startswith('photos/'):
                original_filename = original_filename.replace('photos/', '')
            filename = original_filename
        else:
            # Генерируем имя с timestamp
            filename = f"photo_{message.message_id}_{int(message.date.timestamp())}.jpg"

        success = await user_session.upload_file(file_obj=photo_io, filename=filename)

        if success:
            await message.answer("✅ Фото загружено!")
        else:
            await message.answer("❌ Ошибка загрузки фото")

    except Exception as e:
        await main_logger.error(f"Ошибка загрузки одиночной фотографии: {e}")
        await message.answer(f"❌ Ошибка загрузки фотографии. Попробуйте позже")


@media_downloader.message(F.photo & F.media_group_id)
async def handle_media_group(message: types.Message, bot: Bot):
    """Обработка медиагрупп (альбомов) с учетом пользователя"""
    media_group_id = message.media_group_id
    user_id = message.from_user.id

    # Если это первое медиа в группе
    if media_group_id not in media_groups:
        media_groups[media_group_id] = {
            'user_id': user_id,  # Добавляем ID пользователя
            'messages': [],
            'processed': False,
            'chat_id': message.chat.id
        }

        # Устанавливаем таймер для обработки всей группы
        asyncio.create_task(process_media_group(
            media_group_id=media_group_id,
            bot=bot,
            message_id=message.message_id
        ))

    # Добавляем сообщение в группу
    media_groups[media_group_id]['messages'].append(message)


async def process_media_group(media_group_id: str, bot: Bot, message_id: int):
    """Обработка всей медиагруппы после небольшой задержки"""
    # Ждем 3 секунды, чтобы все медиа группы успели прийти
    await asyncio.sleep(2)

    if media_group_id not in media_groups:
        return

    group_data = media_groups[media_group_id]

    # Если группа уже обработана или пуста - выходим
    if group_data['processed'] or not group_data['messages']:
        return

    group_data['processed'] = True
    messages = group_data['messages']
    chat_id = group_data['chat_id']
    user_id = group_data['user_id']  # Получаем ID пользователя

    try:
        # Получаем сессию пользователя
        user_session = await session_manager.get_user_session(user_id)
        downloaded_files = []

        # Скачиваем все медиа из группы
        for msg in messages:
            if msg.photo:
                photo = msg.photo[-1]
                photo_io = await bot.download(photo.file_id)

                # Генерируем уникальное имя файла с timestamp
                import time
                filename = f"{int(time.time())}_{photo.file_id}.jpg"

                success = await user_session.upload_file(file_obj=photo_io, filename=filename)

                if success:
                    downloaded_files.append(filename)

        # Отправляем итоговое сообщение
        await bot.send_message(
            chat_id=chat_id,
            text=f"✅ Медиагруппа загружена! Файлов: {len(downloaded_files)}\n"
                 f"📁 Папка: {user_session.current_path}",
            reply_to_message_id=message_id
        )

    except Exception as e:
        await main_logger.error(f"Ошибка загрузки медиагруппы: {e}")
        await bot.send_message(chat_id, text="❌ Ошибка загрузки медиагруппы.Попробуйте позже")

    finally:
        # Удаляем обработанную группу из временного хранилища
        if media_group_id in media_groups:
            del media_groups[media_group_id]


@media_downloader.message(F.document)
async def download_document(message: types.Message, bot: Bot):
    """Обработка документов"""
    try:
        user_session = await session_manager.get_user_session(message.from_user.id)

        document = message.document
        file_io = await bot.download(document.file_id)

        success = await user_session.upload_file(
            file_obj=file_io,
            filename=document.file_name or document.file_id
        )

        if success:
            await message.answer("✅ Документ загружен!")
        else:
            await message.answer("❌ Ошибка загрузки документа")

    except Exception as e:
        await main_logger.error(f"Ошибка загрузки документа: {e}")
        await message.answer(f"❌ Ошибка загрузки документа. Попробуйте позже")
