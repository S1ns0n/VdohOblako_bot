from aiogram import Bot, types, F
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from yandex_api.yandex_api import YandexManager
from .keyboards import Keyboards
from .utils import Utils
from config.config import Config
from .disk_manager_router import start_disk

from database.database import (
    create_user,
    get_all_users,
    get_user_by_tg_id,
    delete_user,
    get_user_count,
    check_user_exists
)

class RegState(StatesGroup):
    password = State()


registration_router = Router()
keyboards = Keyboards()


@registration_router.message(Command('start'))
async def start_bot(message: types.Message, bot: Bot):

    loading_msg = await bot.send_message(message.from_user.id, "⏳ Загрузка...")
    if await check_user_exists(message.from_user.id):
        await start_disk(message=message,
                         bot=bot)
        await loading_msg.delete()
        return

    await loading_msg.edit_text(text=f"🔒 Добро пожаловать!\n"
                                    "Этот бот — только для сотрудников АНО «Вдохновители» 🌟.\n\n"
                                    "⚠️ Если вы не сотрудник, пожалуйста, не пытайтесь получить доступ — это не сработает 😉.\n\n"
                                    "📩 Сотрудникам:\n"
                                    "Чтобы получить доступ, напишите @Gllushkoff — он поможет! ✨",
                                reply_markup= await keyboards.new_user_board())



    # await create_user(tg_id=message.from_user.id)
    # await loading_msg.edit_text(
    #     text=f"Вы зареганы!")

@registration_router.callback_query(F.data == "reg_enter_password")
async def start_reg(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    try:
        await bot.edit_message_reply_markup(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=None
        )
    except:
        pass
    await callback.answer()
    await state.set_state(RegState.password)
    await bot.send_message(chat_id=callback.from_user.id,
                           text=f"🔑 Введите пароль для получения доступа:")


@registration_router.message(RegState.password)
async def process_password(message: types.Message, bot: Bot, state: FSMContext):
    if message.text.strip() == Config.PASSWORD:
        await create_user(tg_id=message.from_user.id)
        await state.clear()
        await message.answer(text=f"🎉 Отлично!\n"
                                "Пароль верный — теперь у вас полный доступ! ✅ \n\n"
                                "🌟 <b>Что умеет бот?</b>\n"
                                "Вы можете свободно перемещаться по всем директориям (папкам) Яндекс Диска и загружать туда фотографии.\n\n"
                                
                                "🔍 <b>Как пользоваться?</b>\n"
                                "1️⃣ Найдите нужную папку — перемещайтесь по директориям, чтобы выбрать место для загрузки.\n"
                                "2️⃣ Нажмите «Выбрать папку» — подтвердите выбор папки для загрузки.\n"
                                "3️⃣ Отправьте фотографии — просто скиньте их в чат, и они автоматически загрузятся на Яндекс Диск!\n"
                                "💡 Готово! Ваши фотографии сохранены. 😊",
                             parse_mode=ParseMode.HTML,
                             reply_markup=await keyboards.go_to_disk_board())
    else:
        await message.answer(text=f"🚨 Упс!\n"
                                "Кажется, вы ввели неверный пароль 😬.\n"
                                "🔐 Попробуйте ещё раз или напишите @Gllushkoff, чтобы восстановить доступ.\n")
        return

@registration_router.callback_query(F.data == "go_to_disk")
async def go_to_disk(callback: types.CallbackQuery, bot: Bot):
    await callback.answer()
    await start_disk(message=callback.message,
                     bot=bot)
