import asyncio

from aiogram import Bot, Dispatcher

from bot.disk_manager_router import disk_manager_router
from bot.registration_router import registration_router
from bot.media_block_middleware import MediaBlockMiddleware
from bot.media_download_router import media_downloader
from config.config import Config
from database.session import init_db

async def main() -> None:
    await init_db()
    bot = Bot(token=Config.BOT_TOKEN)
    dp = Dispatcher()
    dp.update.outer_middleware(MediaBlockMiddleware())

    dp.include_router(disk_manager_router)
    dp.include_router(registration_router)
    dp.include_router(media_downloader)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Бот запущен...")
    asyncio.run(main())
