from aiogram.dispatcher.filters.state import StatesGroup, State


class RegistrationState(StatesGroup):
    phone_number = State()
    full_name = State()


class SettingsState(StatesGroup):
	options = State()
	change_language = State()
	change_number = State()


class ShoppingState(StatesGroup):
	catalogs = State()
	product_view = State()


class CartState(StatesGroup):
	opened_cart = State()


class ClickPaymentState(StatesGroup):
	pay_button = State()
	expect_payment = State()

class OrdersState(StatesGroup):
	order_view = State()