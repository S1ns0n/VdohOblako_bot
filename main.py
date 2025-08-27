import asyncio

from aiogram import Bot, Dispatcher

from bot.bot import start_router
from bot.media_block_middleware import MediaBlockMiddleware
from config.config import Config

async def main() -> None:
    bot = Bot(token=Config.BOT_TOKEN)
    dp = Dispatcher()
    dp.update.outer_middleware(MediaBlockMiddleware())

    dp.include_router(start_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Бот запущен...")
    asyncio.run(main())
