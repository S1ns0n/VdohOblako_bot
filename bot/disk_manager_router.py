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


disk_manager_router = Router()
keyboards = Keyboards()

manager = YandexManager(Config.YANDEX_API_TOKEN)


@disk_manager_router.message(Command('disk'))
async def start_bot(message: types.Message, bot: Bot):
    # чо вообще делаем дальше:
    # добовляем статистическую информацию о каждой папке (сколько файлов например) ✅
    # подготовить проект к закидыванию на гитхаб ✅
    # далее делаем клаву с с кнопками назад и выбрать папку, после выбора папки это должно записываться в базу
    # сделать мидлвеир который отлавливает все фото/видео/файлы и проверяет, есть ли у пользователя выбранная папка ✅
    # придумать систему скачки всех файлов в выбранную директорию

    manager.current_path = "/"

    await manager.refresh_current_dir()

    await bot.send_message(message.from_user.id, text=str(manager.current_path),
                           reply_markup=await keyboards.main_welcome_board(folders=manager.folders))


@disk_manager_router.callback_query(F.data.startswith("folder_"))
async def process_dir(call: types.CallbackQuery, bot: Bot):
    dir_index = await Utils.extract_number(call.data)

    # Показываем сообщение о загрузке
    loading_msg = await bot.send_message(call.from_user.id, "⏳ Загрузка...")

    await manager.change_dir(folder_index=dir_index)

    # Редактируем существующее сообщение вместо отправки нового
    await loading_msg.edit_text(
        text=f"{str(manager.current_path)}\n\nФайлов в папке: {await manager.get_files_count()}",
        reply_markup=await keyboards.main_welcome_board(folders=manager.folders)
    )
    await call.answer()


@disk_manager_router.callback_query(F.data.startswith("nav_"))
async def procces_nav(call: types.CallbackQuery, bot: Bot):
    action = call.data

    match action:
        case "nav_back":

            loading_msg = await bot.send_message(call.from_user.id, "⏳ Загрузка...")

            await manager.go_back()

            await loading_msg.edit_text(
                text=f"{str(manager.current_path)}\n\nФайлов в папке: {await manager.get_files_count()}",
                reply_markup=await keyboards.main_welcome_board(folders=manager.folders)
            )
            await call.answer()

        case "nav_select":
            pass



