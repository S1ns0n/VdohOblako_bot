import asyncio
from datetime import datetime
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Update

from database.database import (
    check_user_exists
)

class MediaBlockMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.last_block_time = {}
        self.block_cooldown = 1
        self.locks = {}

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        if not event.message:
            return await handler(event, data)

        message = event.message
        chat_id = message.chat.id
        user_id = message.from_user.id

        # Обработка текстовых сообщений
        if message.content_type in ['text', 'sticker']:
            # Пропускаем команды (текстовые сообщения начинающиеся с '/')
            if message.content_type == 'text' and message.text.startswith('/'):
                return await handler(event, data)

            # Проверяем наличие FSM через state
            state = data.get('state')
            if state:
                current_state = await state.get_state()
                if current_state is not None:
                    # FSM активна - пропускаем обработку
                    return await handler(event, data)

            bot = data['bot']
            await bot.delete_message(
                chat_id=chat_id,
                message_id=message.message_id
            )


        if await check_user_exists(user_id):
            return await handler(event, data)

        if any([
            message.photo, message.video, message.document,
            message.audio, message.voice, message.video_note,
            message.sticker, message.animation
        ]):
            if chat_id not in self.locks:
                self.locks[chat_id] = asyncio.Lock()

            async with self.locks[chat_id]:
                current_time = datetime.now()
                last_block = self.last_block_time.get(chat_id)

                if last_block and (current_time - last_block).total_seconds() < self.block_cooldown:
                    return

                bot = data['bot']
                await bot.send_message(
                    chat_id=chat_id,
                    text="Нет доступа"
                )

                self.last_block_time[chat_id] = current_time
            return

        return await handler(event, data)