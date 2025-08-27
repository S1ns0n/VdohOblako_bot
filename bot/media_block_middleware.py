from aiogram import BaseMiddleware
from aiogram.types import Update
from typing import Callable, Dict, Any, Awaitable

class MediaBlockMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        # Проверяем, что это сообщение и оно содержит медиа
        if event.message and event.message.content_type != 'text':
            bot = data['bot']
            await bot.send_message(
                chat_id=event.message.chat.id,
                text="Нет доступа"
            )
            return  # Прерываем обработку

        return await handler(event, data)
