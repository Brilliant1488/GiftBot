from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger


class PaymentStates(StatesGroup):
    """Состояния FSM для оплаты."""
    waiting_for_usdt_hash = State()
    waiting_for_card_receipt = State()
    waiting_for_transaction_hash = State()


class PaymentHandler:
    """Класс для обработки логики оплаты."""

    @staticmethod
    async def handle_pay_usdt(callback_query: CallbackQuery, state: FSMContext):
        """Обработка кнопки оплаты USDT."""
        try:
            logger.info(f"Пользователь {callback_query.from_user.id} выбрал оплату USDT.")

            # Устанавливаем состояние ожидания хэша
            await state.set_state(PaymentStates.waiting_for_transaction_hash)

            # Обновляем сообщение вместо отправки нового
            await callback_query.message.edit_text(
                text=(
                    "💵 **Для оплаты USDT (TRC20):**\n\n"
                    f"Адрес кошелька: `T123abc456def789ghi`\n\n"
                    "📌 Убедитесь, что переводите средства по сети **TRC20**.\n\n"
                    "После перевода введите хэш транзакции сюда."
                ),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.exception(f"Ошибка обработки оплаты USDT: {e}")
            await callback_query.message.reply("❌ Произошла ошибка. Попробуйте снова.")

    @staticmethod
    async def handle_paid_card(callback_query: CallbackQuery, state: FSMContext):
        """Обработка кнопки 'Оплатил' для перевода на карту."""
        logger.info(f"Пользователь {callback_query.from_user.id} выбрал перевод на карту.")
        await callback_query.message.reply(
            text="📄 Пожалуйста, отправьте квитанцию об оплате (скриншот или файл)."
        )
        await state.set_state(PaymentStates.waiting_for_card_receipt)

    @staticmethod
    async def handle_paid_usdt(callback_query: CallbackQuery, state: FSMContext):
        """Обработка кнопки 'Оплатил' для USDT."""
        try:
            logger.info(f"Пользователь {callback_query.from_user.id} нажал 'Оплатил' для USDT.")

            # Проверка состояния FSM
            current_state = await state.get_state()
            if current_state != PaymentStates.waiting_for_transaction_hash.state:
                await callback_query.message.reply("❌ Я не ожидаю хэш транзакции. Следуйте инструкциям.")
                return

            # Сбрасываем состояние
            await state.clear()

            # Уведомляем пользователя
            await callback_query.message.reply("✅ Спасибо! Ваш платеж принят, ожидайте подтверждения.")
        except Exception as e:
            logger.exception(f"Ошибка обработки кнопки 'Оплатил' для USDT: {e}")
            await callback_query.message.reply("❌ Произошла ошибка. Попробуйте снова.")

    @staticmethod
    async def handle_receipt(message: Message, state: FSMContext):
        """Обработка отправленной квитанции."""
        current_state = await state.get_state()
        if current_state != PaymentStates.waiting_for_card_receipt:
            await message.reply(
                text="❌ Некорректное действие. Я не ожидаю квитанцию. Пожалуйста, следуйте инструкциям."
            )
            return

        user_id = message.from_user.id
        if message.photo:
            logger.info(f"Пользователь {user_id} отправил квитанцию в виде фото.")
            await message.reply(
                text="✅ Ваша квитанция принята. Ожидайте подтверждение оплаты. Это может занять до 10 минут."
            )
            await state.clear()
        elif message.document:
            logger.info(f"Пользователь {user_id} отправил квитанцию в виде документа.")
            await message.reply(
                text="✅ Ваша квитанция принята. Ожидайте подтверждение оплаты. Это может занять до 10 минут."
            )
            await state.clear()
        else:
            logger.warning(f"Пользователь {user_id} отправил некорректное сообщение вместо квитанции.")
            await message.reply(
                text="❌ Некорректный формат квитанции. Пожалуйста, отправьте скриншот или файл."
            )
