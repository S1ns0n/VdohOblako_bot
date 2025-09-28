from aiogram import Bot, types, F
from aiogram import Router
from aiogram.filters import Command
from aiogram.enums import ParseMode

from yandex_api.yandex_api import SessionManager
from .keyboards import Keyboards
from .utils import Utils
from config.config import Config


from database.database import (
    create_user,
    get_all_users,
    get_user_by_tg_id,
    delete_user,
    get_user_count,
    update_user_path
)


disk_manager_router = Router()
keyboards = Keyboards()

session_manager = SessionManager(Config.YANDEX_API_TOKEN)

@disk_manager_router.message(Command('path'))
async def get_path(message: types.Message):
    user_session = await session_manager.get_user_session(message.chat.id)
    await message.delete()
    await message.answer(text=f"💾 Ваш путь для сохранения: {user_session.current_path}")


@disk_manager_router.message(Command('disk'))
async def start_disk(message: types.Message, bot: Bot):
    user_session = await session_manager.get_user_session(message.chat.id)

    await message.delete()
    loading_msg = await bot.send_message(chat_id=message.chat.id, text="⏳ Загрузка...")

    await user_session.refresh_current_dir()

    await loading_msg.edit_text(
        text=str(user_session.current_path),
        reply_markup=await keyboards.main_welcome_board(folders=user_session.folders)
    )


@disk_manager_router.callback_query(F.data.startswith("folder_"))
async def process_dir(call: types.CallbackQuery, bot: Bot):
    user_session = await session_manager.get_user_session(call.message.chat.id)
    dir_index = await Utils.extract_number(call.data)

    loading_msg = await bot.edit_message_text(chat_id=call.message.chat.id, text="⏳ Загрузка...", message_id=call.message.message_id)

    await user_session.change_dir(folder_index=dir_index)

    await loading_msg.edit_text(
        text=f"{str(user_session.current_path)}\n\nФайлов в папке: {await user_session.get_files_count()}",
        reply_markup=await keyboards.main_welcome_board(folders=user_session.folders)
    )
    await call.answer()


@disk_manager_router.callback_query(F.data.startswith("nav_"))
async def procces_nav(call: types.CallbackQuery, bot: Bot):
    user_session = await session_manager.get_user_session(call.message.chat.id)
    action = call.data
    loading_msg = await bot.edit_message_text(chat_id=call.message.chat.id, text="⏳ Загрузка...", message_id=call.message.message_id)

    match action:
        case "nav_back":
            await user_session.go_back()

            await loading_msg.edit_text(
                text=f"{str(user_session.current_path)}\n\nФайлов в папке: {await user_session.get_files_count()}",
                reply_markup=await keyboards.main_welcome_board(folders=user_session.folders)
            )

        case "nav_select":
            await update_user_path(
                tg_id=call.from_user.id,
                path=user_session.current_path
            )

            await loading_msg.edit_text(
                text="🎯 <b>Путь выбран успешно!</b>\n\n"
                     "📸 Теперь вы можете скидывать фотографии и другие медиафайлы",
                parse_mode=ParseMode.HTML
            )
        case "nav_root":
            user_session.current_path = "/"
            await user_session.refresh_current_dir()

            await loading_msg.edit_text(
                text=str(user_session.current_path),
                reply_markup=await keyboards.main_welcome_board(folders=user_session.folders)
            )

    await call.answer()


