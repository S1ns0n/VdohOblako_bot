from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


class Keyboards:

    @staticmethod
    async def main_welcome_board(folders: list) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.row(
            InlineKeyboardButton(text="◀️ Назад", callback_data="nav_back"),
            InlineKeyboardButton(text="✅ Выбрать папку", callback_data="nav_select"),
        InlineKeyboardButton(text="#️⃣ В Корень", callback_data="nav_root")
        )


        for i, folder in enumerate(folders, 1):
            builder.button(text=f"📁 {folder}", callback_data=f"folder_{i}")

        builder.adjust(2, *[1] * len(folders))

        return builder.as_markup()

    @staticmethod
    async def new_user_board() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.row(
            InlineKeyboardButton(text="🔒 Ввести пароль", callback_data="reg_enter_password"),
        )

        return builder.as_markup()

    @staticmethod
    async def go_to_disk_board() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.row(
            InlineKeyboardButton(text="💾 Диск", callback_data="go_to_disk"),
        )

        return builder.as_markup()