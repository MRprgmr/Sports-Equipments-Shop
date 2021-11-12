import pytz
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from django.conf import settings

from Bot.models import Category, Order, User, Product
from data.config import CONTACT_NUMBER as contact_number
from localization.strings import _
from utils.core import calculate_total_cost

media_root = settings.MEDIA_ROOT

# CallBack datas
product_view_callback = CallbackData(
    'product_view', 'category_id', 'product_number')
add_to_cart = CallbackData('add_to_cart', 'product_id')
remove_from_cart = CallbackData('remove_from_cart', 'product_id', 'current_number')
product_in_cart = CallbackData('product_in_cart', 'product_id')
orders_button = CallbackData('orders', 'order_id')


def make_product_view_template(user: User, category: Category, product_number):
    """Return product image with its details"""

    products = category.products.all()
    count = products.count()

    if count == 0:
        return "empty", 0, 0

    product: Product = products[product_number]
    id = product_number

    text = _('product_template', user.lang).format(title=product.title,
                                                   description=product.description,
                                                   link=product.link,
                                                   phone_number=contact_number,
                                                   price=product.price,
                                                   currency=product.currency)

    keyboard = InlineKeyboardMarkup(row_width=3)
    if id == 0:
        previous_button = "null"
    else:
        previous_button = product_view_callback.new(
            category_id=category.id, product_number=id - 1)
    if id == count - 1:
        next_button = "null"
    else:
        next_button = product_view_callback.new(
            category_id=category.id, product_number=id + 1)
    keyboard.add(
        InlineKeyboardButton(text="<",
                             callback_data=previous_button,
                             ),
        InlineKeyboardButton(text=f"{id + 1}/{count}",
                             callback_data="null",
                             ),
        InlineKeyboardButton(text=">",
                             callback_data=next_button,
                             )
    )
    if product in user.product_cart.all():
        add_to_cart_button = InlineKeyboardButton(
            text=_('go_to_cart_btn', user.lang), callback_data='product_cart')
    else:
        add_to_cart_button = InlineKeyboardButton(
            text=_('add_cart_btn', user.lang), callback_data=add_to_cart.new(product_id=product.id))
    keyboard.add(add_to_cart_button)

    photo = open(f"{media_root}/{product.image}", 'rb')

    return text, keyboard, photo


def make_cart_view_template(user: User, id):
    """Return saved products templates"""

    products = user.product_cart.all()
    count = products.count()

    if count == 0:
        return "empty", 0, 0

    product = products[id]

    text = _('product_template', user.lang).format(title=product.title,
                                                   description=product.description,
                                                   link=product.link,
                                                   phone_number=contact_number,
                                                   price=product.price,
                                                   currency=product.currency)

    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(InlineKeyboardButton(text=_('remove_from_cart_btn', user.lang),
                                      callback_data=remove_from_cart.new(product_id=product.id, current_number=id)))
    if id == 0:
        previous_button = "null"
    else:
        previous_button = product_in_cart.new(product_id=id - 1)
    if id == count - 1:
        next_button = "null"
    else:
        next_button = product_in_cart.new(product_id=id + 1)
    keyboard.add(
        InlineKeyboardButton(text="◀️",
                             callback_data=previous_button,
                             ),
        InlineKeyboardButton(text=f"{id + 1}/{count}",
                             callback_data="null",
                             ),
        InlineKeyboardButton(text="▶️",
                             callback_data=next_button,
                             )
    )
    total_payment = calculate_total_cost(products=products)

    keyboard.add(InlineKeyboardButton(text=f"💳  {total_payment}",
                                      callback_data="make_payment"))

    photo = open(f"{media_root}/{product.image}", 'rb')

    return text, keyboard, photo


def get_payment_buttons(user, products):
    """Return pay and cancel button for the payment message"""

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text=f"{_('pay', user.lang)} {calculate_total_cost(products=products)}", pay=True))
    keyboard.add(InlineKeyboardButton(text=_('cancel_payment', user.lang), callback_data="cancel_payment"))
    return keyboard


def make_orders_view_template(user: User, id):
    """Return user orders template"""

    orders = user.orders.all()
    count = orders.count()

    if count == 0:
        return "empty", 0

    order: Order = orders[id]

    text = _('order_info_template', user.lang).format(order_id=order.id,
                                                      paid_money=f"{order.total_cost} so'm",
                                                      payment_time=order.creation_date.astimezone(
                                                          pytz.timezone('Asia/Tashkent')).strftime('%d/%m/%Y, %H:%M'),
                                                      address=order.address_location,
                                                      ordered_products=order.products_list)

    keyboard = InlineKeyboardMarkup(row_width=3)
    if id == 0:
        previous_button = "null"
    else:
        previous_button = orders_button.new(order_id=id - 1)
    if id == count - 1:
        next_button = "null"
    else:
        next_button = orders_button.new(order_id=id + 1)
    keyboard.add(
        InlineKeyboardButton(text="◀️",
                             callback_data=previous_button,
                             ),
        InlineKeyboardButton(text=f"{id + 1}/{count}",
                             callback_data="null",
                             ),
        InlineKeyboardButton(text="▶️",
                             callback_data=next_button,
                             )
    )
    keyboard.add(InlineKeyboardButton(text=_('back', user.lang), callback_data='back'))

    return text, keyboard
