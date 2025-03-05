from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from loguru import logger

from OrderManager import order_manager
from PaymentHandler import PaymentStates
from config import CARD_DETAILS, USDT_WALLET_ADDRESS, bot, WELCOME_IMAGE_URL
from instruction_manager import InstructionManager  # Для работы с инструкциями


class MenuHandler:
    """Класс для обработки меню и взаимодействий с пользователем."""

    @staticmethod
    async def send_welcome(message: Message):
        """Отправляет приветственное сообщение с восстановленным меню."""
        try:
            logger.info(f"Пользователь {message.from_user.id} вызвал приветствие.")
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🎁 Купить Gift-код", callback_data="select_category")],
                    [InlineKeyboardButton(text="🛠 Техподдержка", callback_data="support")],
                ]
            )
            await bot.send_photo(
                chat_id=message.chat.id,
                photo=WELCOME_IMAGE_URL,
                caption=(
                    "👋 Добро пожаловать в наш сервис обмена Gift-кодов!\n\n"
                    "💳 Вы можете приобрести коды для:\n"
                    "• 🛒 Binance\n"
                    "• 🎮 Steam\n"
                    "• 📺 Netflix\n"
                    "• 🎮 Xbox\n"
                    "• 🎵 Spotify\n"
                    "• 🎮 PlayStation Store\n"
                    "• 🍎 ITunes\n"
                    "• 📦 Amazon\n"
                    "• 🎮 EA Gift Card\n\n"
                    "💡 Надёжно, быстро и удобно!\n\n"
                    "👇 Выберите действие ниже:"
                ),
                reply_markup=keyboard
            )
        except Exception as e:
            logger.exception(f"Ошибка отправки приветствия: {e}")
            await message.reply("❌ Ошибка! Попробуйте позже.")

    @staticmethod
    async def select_category(callback_query: CallbackQuery):
        """Отображает меню выбора категорий."""
        try:
            logger.info(f"Пользователь {callback_query.from_user.id} открыл меню категорий.")

            # Создаем клавиатуру с уникальными callback_data для каждой категории
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="EA Gift Card", callback_data="category_ea")],
                    [InlineKeyboardButton(text="Steam", callback_data="category_steam")],
                    [InlineKeyboardButton(text="Binance", callback_data="category_binance")],
                    [InlineKeyboardButton(text="Netflix", callback_data="category_netflix")],
                    [InlineKeyboardButton(text="Xbox", callback_data="category_xbox")],
                    [InlineKeyboardButton(text="Spotify", callback_data="category_spotify")],
                    [InlineKeyboardButton(text="PlayStation Store", callback_data="category_playstation")],
                    [InlineKeyboardButton(text="ITunes", callback_data="category_itunes")],
                    [InlineKeyboardButton(text="Amazon", callback_data="category_amazon")],
                    [InlineKeyboardButton(text="⬅️ Вернуться", callback_data="main_menu")],
                ]
            )

            # Проверяем, можно ли изменить сообщение
            if callback_query.message.text:
                await bot.edit_message_text(
                    chat_id=callback_query.message.chat.id,
                    message_id=callback_query.message.message_id,
                    text="🎁 Выберите категорию:",
                    reply_markup=keyboard
                )
            else:
                await bot.send_message(
                    chat_id=callback_query.message.chat.id,
                    text="🎁 Выберите категорию:",
                    reply_markup=keyboard
                )
        except Exception as e:
            logger.exception(f"Ошибка в select_category: {e}")
            await callback_query.message.reply("❌ Ошибка! Попробуйте позже.")

    @staticmethod
    async def show_instruction_menu(callback_query: CallbackQuery, category: str):
        """Отображает меню с инструкцией для выбранной категории."""
        try:
            logger.info(f"Пользователь {callback_query.from_user.id} открыл инструкцию для категории: {category}")
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="📖 Инструкция активации", callback_data=f"show_instruction_{category}")],
                    [InlineKeyboardButton(text="✅ Ознакомлен с инструкцией", callback_data=f"confirm_{category}_0")],
                    [InlineKeyboardButton(text="⬅️ Вернуться", callback_data="select_category")],
                ]
            )
            await callback_query.message.edit_text(
                f"Категория: {category.capitalize()}.\n\n"
                "Пожалуйста, ознакомьтесь с инструкцией активации перед продолжением.",
                reply_markup=keyboard
            )
        except Exception as e:
            logger.exception(f"Ошибка отображения меню инструкций для {category}: {e}")
            await callback_query.message.reply("❌ Ошибка! Попробуйте позже.")

    @staticmethod
    async def select_amount_menu(callback_query: CallbackQuery, category: str):
        """Отображает меню выбора суммы для категории."""
        try:
            logger.info(f"Пользователь {callback_query.from_user.id} открыл меню выбора суммы для категории {category}.")
            amounts = [5, 15, 25, 50, 100, 150, 200, 350, 500, 1000]

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=f"{amount} USD", callback_data=f"amount_{category}_{amount}")]
                    for amount in amounts
                ] + [[InlineKeyboardButton(text="⬅️ Вернуться", callback_data="select_category")]]
            )

            await callback_query.message.edit_text(
                f"Категория: {category.capitalize()}.\n\nВыберите сумму покупки:",
                reply_markup=keyboard
            )
        except Exception as e:
            logger.exception(f"Ошибка отображения меню выбора суммы для категории {category}: {e}")
            await callback_query.message.reply("❌ Ошибка! Попробуйте снова.")

    @staticmethod
    async def confirm_amount(callback_query: CallbackQuery):
        """Подтверждает сумму и предлагает способы оплаты."""
        try:
            data = callback_query.data.split("_")
            if len(data) != 3:
                raise ValueError("Некорректный формат данных callback_query.")

            _, category, amount = data
            logger.info(f"Пользователь {callback_query.from_user.id} выбрал {amount} USD в категории {category}.")

            # Создаем заказ
            order_manager.create_order(callback_query.from_user.id, category, int(amount))

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="💳 Оплата СБП", callback_data="pay_sbp")],
                    [InlineKeyboardButton(text="📷 СБП QR", callback_data="pay_sbp_qr")],
                    [InlineKeyboardButton(text="💳 Перевод на карту", callback_data="pay_card")],
                    [InlineKeyboardButton(text="💵 Оплата USDT (TRC20)", callback_data="pay_usdt")],
                    [InlineKeyboardButton(text="⬅️ Вернуться", callback_data=f"select_category")],
                ]
            )

            await callback_query.message.edit_text(
                f"💵 Сумма: {amount} USD\n👇 Выберите способ оплаты:",
                reply_markup=keyboard
            )
        except Exception as e:
            logger.exception(f"Ошибка подтверждения суммы: {e}")
            await callback_query.message.reply("❌ Ошибка! Попробуйте снова.")

    @staticmethod
    async def handle_payment_choice(callback_query: CallbackQuery):
        """Обрабатывает выбор способа оплаты."""
        try:
            if callback_query.data == "pay_usdt":
                logger.info(f"Пользователь {callback_query.from_user.id} выбрал оплату USDT.")
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="✅ Оплатил", callback_data="paid_usdt")],
                        [InlineKeyboardButton(text="⬅️ Вернуться", callback_data="select_category")],
                    ]
                )
                await callback_query.message.edit_text(
                    text=(
                        "💵 **Для оплаты USDT (TRC20):**\n\n"
                        f"Адрес кошелька: `{USDT_WALLET_ADDRESS}`\n\n"
                        "📌 Убедитесь, что переводите средства по сети **TRC20**."
                    ),
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
            elif callback_query.data == "pay_card":
                logger.info(f"Пользователь {callback_query.from_user.id} выбрал оплату картой.")
                await callback_query.message.edit_text(
                    text=(
                        "💳 **Для перевода на карту:**\n\n"
                        f"{CARD_DETAILS}\n\n"
                        "📌 После перевода напишите нам для подтверждения платежа."
                    )
                )
            else:
                logger.warning(f"Некорректный способ оплаты: {callback_query.data}")
                await callback_query.message.reply("❌ Этот способ оплаты недоступен.")
        except Exception as e:
            logger.error(f"Ошибка обработки способа оплаты: {e}")
            await callback_query.message.reply("❌ Ошибка! Попробуйте позже.")

    @staticmethod
    async def handle_receipt(message: Message, state: FSMContext):
        """Обрабатывает квитанции от пользователя."""
        try:
            current_state = await state.get_state()
            if current_state != PaymentStates.waiting_for_card_receipt.state:
                await message.reply("❌ Мы не ожидаем квитанцию сейчас.")
                return

            if message.photo or message.document:
                logger.info(f"Квитанция от пользователя {message.from_user.id} принята.")
                await message.reply("✅ Ваша квитанция принята! Ожидайте подтверждения.")
                await state.clear()
            else:
                logger.warning(f"Пользователь {message.from_user.id} отправил некорректный формат вместо квитанции.")
                await message.reply("❌ Неверный формат. Пожалуйста, отправьте скриншот или файл.")
        except Exception as e:
            logger.exception(f"Ошибка обработки квитанции: {e}")
            await message.reply("❌ Ошибка! Попробуйте позже.")