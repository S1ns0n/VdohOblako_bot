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
            InlineKeyboardButton(text="✅ Выбрать папку", callback_data="nav_select")
        )


        for i, folder in enumerate(folders, 1):
            builder.button(text=f"📁 {folder}", callback_data=f"folder_{i}")

        builder.adjust(2, *[1] * len(folders))

        return builder.as_markup()
