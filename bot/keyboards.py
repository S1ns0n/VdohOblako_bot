from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


class Keyboards:

    @staticmethod
    async def main_welcome_board(folders: list) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        # Первые две кнопки в одном ряду
        builder.row(
            InlineKeyboardButton(text="◀️ Назад", callback_data="nav_back"),
            InlineKeyboardButton(text="✅ Выбрать папку", callback_data="nav_select")
        )

        # Кнопки папок (каждая в своем ряду)
        for i, folder in enumerate(folders, 1):
            builder.button(text=f"📁 {folder}", callback_data=f"folder_{i}")

        # Указываем что все последующие кнопки должны быть по 1 в ряду
        builder.adjust(2, *[1] * len(folders))

        return builder.as_markup()
