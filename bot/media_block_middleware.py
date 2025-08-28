import asyncio
from datetime import datetime
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Update


class MediaBlockMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.last_block_time = {}
        self.block_cooldown = 2
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

        # Проверяем наличие медиа
        if any([
            message.photo, message.video, message.document,
            message.audio, message.voice, message.video_note,
            message.sticker, message.animation
        ]):
            # Создаем lock для этого чата если его нет
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
