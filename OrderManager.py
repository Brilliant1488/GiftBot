from loguru import logger


class OrderManager:
    """Класс для управления заказами."""

    def __init__(self):
        self.orders = {}

    def create_order(self, user_id, category, amount):
        """Создаёт заказ для пользователя."""
        if not isinstance(amount, (int, float)) or amount <= 0:
            logger.warning(f"Попытка создать заказ с некорректной суммой: {amount} USD")
            return False

        self.orders[user_id] = {"category": category, "amount": amount}
        logger.info(f"Создан заказ: Пользователь {user_id}, Категория {category}, Сумма {amount} USD")
        return True

    def get_order(self, user_id):
        """Получает заказ для пользователя."""
        order = self.orders.get(user_id)
        if not order:
            logger.warning(f"Заказ для пользователя {user_id} не найден")
        return order

    def clear_order(self, user_id):
        """Удаляет заказ пользователя."""
        if user_id in self.orders:
            del self.orders[user_id]
            logger.info(f"Заказ пользователя {user_id} удалён")
            return True
        logger.warning(f"Попытка удалить несуществующий заказ пользователя {user_id}")
        return False


# Инициализация менеджера заказов
order_manager = OrderManager()
