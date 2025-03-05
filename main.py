import asyncio
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message
from loguru import logger
from aiogram import F, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from config import bot, CARD_DETAILS, USDT_WALLET_ADDRESS
from PaymentHandler import PaymentHandler, PaymentStates
from MenuHandler import MenuHandler
from instruction_manager import InstructionManager

# Инициализация памяти FSM
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Регистрация обработчиков
def register_handlers():
    """Регистрация всех обработчиков."""
    # Callback'и
    dp.callback_query.register(MenuHandler.confirm_amount, lambda c: c.data.startswith("amount_"))
    dp.callback_query.register(MenuHandler.select_category, lambda c: c.data.startswith("category_"))
    dp.callback_query.register(handle_support, lambda c: c.data == "support")
    dp.callback_query.register(handle_category_selection, lambda c: c.data.startswith("category_"))
    dp.callback_query.register(confirm_instruction_handler, lambda c: c.data.startswith("confirm_"))
    dp.callback_query.register(handle_select_category, lambda c: c.data == "select_category")
    dp.callback_query.register(paid_usdt_handler, lambda c: c.data == "paid_usdt")
    dp.callback_query.register(paid_card_handler, lambda c: c.data == "paid_card")

    # Сообщения
    dp.message.register(start_handler, Command("start"))
    dp.message.register(transaction_hash_handler, F.content_type == "text")
    dp.message.register(receipt_handler, F.content_type.in_({"photo", "document"}))


# Обработчик команды /start
async def start_handler(message: Message, state: FSMContext):
    """Обработка команды /start."""
    logger.info(f"Пользователь {message.from_user.id} вызвал команду /start")
    try:
        await state.clear()  # Сбрасываем состояние FSM
        await MenuHandler.send_welcome(message)
    except Exception as e:
        logger.error(f"Ошибка в обработчике /start: {e}")
        await message.reply("Произошла ошибка. Попробуйте снова позже.")


# Обработчик кнопки "Техподдержка"
async def handle_support(callback_query: CallbackQuery):
    """Обработка нажатия на кнопку 'Техподдержка'."""
    try:
        await callback_query.message.edit_text(
            "📧 Если у вас есть вопросы, свяжитесь с нами:\n"
            "✉️ Email: support@example.com\n"
            "📞 Телеграм: @support_bot",
        )
    except Exception as e:
        logger.exception(f"Ошибка обработки кнопки 'Техподдержка': {e}")
        await callback_query.message.reply("Произошла ошибка. Попробуйте снова.")

# Обработчик для выбора категории
@dp.callback_query(lambda c: c.data.startswith("category_"))
async def handle_category_selection(callback_query: CallbackQuery):
    """Обработка выбора категории пользователем."""
    try:
        # Извлекаем категорию из callback_data
        category_name = callback_query.data.split("_")[1]
        logger.info(f"Пользователь {callback_query.from_user.id} выбрал категорию: {category_name}")

        # Отправляем пользователя на инструкцию для выбранной категории
        await MenuHandler.show_instruction_menu(callback_query, category_name)
    except Exception as e:
        logger.exception(f"Ошибка обработки выбора категории: {e}")
        await callback_query.message.reply("❌ Произошла ошибка. Попробуйте снова.")

@dp.callback_query(lambda c: c.data.startswith("show_instruction_"))
async def show_instruction_handler(callback_query: CallbackQuery):
    """Обработка нажатия на кнопку 'Инструкция активации'."""
    try:
        category_name = callback_query.data.split("_")[2]  # Получаем категорию из callback_data
        logger.info(f"Пользователь {callback_query.from_user.id} запросил инструкцию для категории {category_name}")
        await InstructionManager.send_instruction(callback_query, category_name)
    except Exception as e:
        logger.error(f"Ошибка обработки инструкции для категории: {e}")
        await callback_query.message.reply("❌ Ошибка! Попробуйте снова.")

# Обработчик подтверждения инструкции
@dp.callback_query(lambda c: c.data.startswith("confirm_"))
async def confirm_instruction_handler(callback_query: CallbackQuery):
    """Обработка кнопки 'Ознакомлен с инструкцией'."""
    category_name = callback_query.data.split("_")[1]
    logger.info(f"Пользователь {callback_query.from_user.id} подтвердил ознакомление с инструкцией для категории {category_name}")
    try:
        # Переход к выбору суммы
        await MenuHandler.select_amount_menu(callback_query, category_name)
    except Exception as e:
        logger.error(f"Ошибка при подтверждении инструкции для категории {category_name}: {e}")
        await callback_query.message.reply("Произошла ошибка. Попробуйте снова.")

# Обработчики кнопок оплаты
@dp.callback_query(lambda c: c.data == "pay_sbp")
async def handle_pay_sbp(callback_query: CallbackQuery):
    await callback_query.message.reply("⚠️ Этот способ оплаты пока не поддерживается. Попробуйте другой.")

@dp.callback_query(lambda c: c.data == "pay_sbp_qr")
async def handle_pay_sbp_qr(callback_query: CallbackQuery):
    await callback_query.message.reply("⚠️ Этот способ оплаты пока не поддерживается. Попробуйте другой.")

@dp.callback_query(lambda c: c.data == "pay_card")
async def handle_pay_card(callback_query: CallbackQuery):
    await callback_query.message.reply(
        "💳 **Для перевода на карту:**\n\n"
        f"{CARD_DETAILS}\n\n"
        "📌 После перевода напишите нам для подтверждения платежа."
    )

@dp.callback_query(lambda c: c.data == "pay_usdt")
async def handle_pay_usdt(callback_query: CallbackQuery):
    await callback_query.message.reply(
        "💵 **Для оплаты USDT (TRC20):**\n\n"
        f"Адрес кошелька: `{USDT_WALLET_ADDRESS}`\n\n"
        "📌 Убедитесь, что переводите средства по сети **TRC20**. Учитывайте комиссию при переводе!"
    )



# Обработчик кнопки "Купить Gift-код"
async def handle_select_category(callback_query: CallbackQuery):
    """Обработка нажатия на кнопку 'Купить Gift-код'."""
    try:
        logger.info(f"Пользователь {callback_query.from_user.id} выбрал 'Купить Gift-код'.")
        await MenuHandler.select_category(callback_query)
    except Exception as e:
        logger.exception(f"Ошибка обработки кнопки 'Купить Gift-код': {e}")
        await callback_query.message.reply("❌ Произошла ошибка. Попробуйте снова.")


# Обработчик кнопки "Оплатил" для USDT
@dp.callback_query(lambda c: c.data == "paid_usdt")
async def paid_usdt_handler(callback_query: CallbackQuery, state: FSMContext):
    """Обработка кнопки 'Оплатил' для USDT."""
    try:
        await PaymentHandler.handle_paid_usdt(callback_query, state)
    except Exception as e:
        logger.error(f"Ошибка обработки оплаты USDT: {e}")
        await callback_query.message.reply("❌ Произошла ошибка. Попробуйте снова.")


# Обработчик текста для хеша перевода
@dp.message(StateFilter(PaymentStates.waiting_for_transaction_hash))  # Фильтр по состоянию
async def transaction_hash_handler(message: Message, state: FSMContext):
    """Обработка хэша транзакции."""
    try:
        transaction_hash = message.text.strip()
        logger.info(f"Получен хэш от пользователя {message.from_user.id}: {transaction_hash}")

        # Проверяем формат хэша (например, длина 64 символа)
        if len(transaction_hash) != 64 or not all(c in "0123456789abcdef" for c in transaction_hash):
            await message.reply("❌ Неверный формат хэша. Убедитесь, что это 64-символьный хэш.")
            return

        # Сбрасываем состояние
        await state.clear()

        # Уведомляем пользователя об успешной обработке
        await message.reply("✅ Ваш хэш успешно принят! Ожидайте подтверждения транзакции от оператора.")
    except Exception as e:
        logger.exception(f"Ошибка обработки хэша транзакции: {e}")
        await message.reply("❌ Произошла ошибка. Попробуйте снова.")


# Обработчик кнопки "Оплатил" для перевода на карту
async def paid_card_handler(callback_query: CallbackQuery, state: FSMContext):
    """Обработка кнопки 'Оплатил' для перевода на карту."""
    try:
        await PaymentHandler.handle_paid_card(callback_query, state)
    except Exception as e:
        logger.error(f"Ошибка обработки оплаты через карту: {e}")
        await callback_query.message.reply("Произошла ошибка. Попробуйте снова.")


# Обработчик квитанции (фото или документ)
async def receipt_handler(message: Message, state: FSMContext):
    """Обрабатывает квитанции от пользователя."""
    try:
        await PaymentHandler.handle_receipt(message, state)
    except Exception as e:
        logger.error(f"Ошибка обработки квитанции: {e}")
        await message.reply("Произошла ошибка. Попробуйте снова.")


# Главная точка входа
async def main():
    """Главный метод запуска бота."""
    logger.info("Запуск бота...")
    register_handlers()  # Регистрация обработчиков
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
