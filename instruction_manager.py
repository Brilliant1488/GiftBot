from aiogram.types import CallbackQuery
from loguru import logger
from config import bot
import os


class InstructionManager:
    """Класс для работы с инструкциями."""

    INSTRUCTIONS_PATH = r"C:\Users\Brilliant\PycharmProjects\BotShop\instructions"

    @staticmethod
    async def send_instruction(callback_query: CallbackQuery, category_name: str):
        """Отправляет текстовую инструкцию для указанной категории."""
        try:
            # Формируем путь к файлу инструкции
            file_path_txt = os.path.join(InstructionManager.INSTRUCTIONS_PATH, f"{category_name}.txt")
            logger.info(f"Ищем инструкцию по пути: {file_path_txt}")

            if os.path.exists(file_path_txt):
                # Читаем файл инструкции
                with open(file_path_txt, "r", encoding="utf-8") as file:
                    instructions = file.read()

                # Отправляем текст инструкции
                await callback_query.message.reply(
                    text=f"📄 Инструкция для категории: {category_name.capitalize()}\n\n{instructions}",
                    reply_markup=InstructionManager.get_back_keyboard()
                )
            else:
                logger.warning(f"Инструкция для категории '{category_name}' не найдена.")
                await callback_query.message.reply(
                    "⚠️ Инструкция для этой категории пока недоступна.",
                    reply_markup=InstructionManager.get_back_keyboard()
                )
        except Exception as e:
            logger.error(f"Ошибка при отправке инструкции для категории '{category_name}': {e}")
            await callback_query.message.reply(
                "❌ Произошла ошибка при загрузке инструкции. Обратитесь в поддержку."
            )

    @staticmethod
    def get_back_keyboard():
        """Клавиатура с кнопкой 'Вернуться'."""
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="⬅️ Вернуться", callback_data="select_category")]]
        )
