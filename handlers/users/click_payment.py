import logging
from datetime import datetime

from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.types.message import ContentTypes
from aiogram.types.reply_keyboard import ReplyKeyboardRemove

from Bot.models import Order, User
from data.config import CONTACT_NUMBER as contact_number
from data.config import PAYMENT_PROVIDER, ORDERS_GROUP, CONTACT_NUMBER
from keyboards.inline.private_templates import get_payment_buttons
from loader import dp, bot
from localization.strings import _
from states.private_states import CartState, ClickPaymentState
from utils.core import get_user, send_main_menu, stoa
from utils.currency import usd_in_uzs

shipping_options = {
    'courtyard_house': 'Hovli uy',
    'apartment': 'Kvartira'
}


def get_label_prices(products):
    """Return label of prices of products for the invoice"""

    prices = []
    for product in products:
        if product.currency == '$':
            prices.append(types.LabeledPrice(label=product.title,
                                             amount=product.price * usd_in_uzs * 100))
        else:
            prices.append(types.LabeledPrice(
                label=product.title, amount=product.price * 100))

    return prices


def get_shipping_options(user):
    shipping_options = [
        types.ShippingOption(id='courtyard_house', title=_('to_courtyard_house', user.lang)).add(
            types.LabeledPrice(_('delivering', user.lang), 0)),
        types.ShippingOption(id='apartment', title=_('to_apartment', user.lang)).add(
            types.LabeledPrice(_('delivering', user.lang), 0)),
    ]
    return shipping_options


@dp.callback_query_handler(text='make_payment', state=CartState.opened_cart)
async def send_payment_invoice(call: types.CallbackQuery):
    """When user press pay button in cart"""

    user: User = await get_user(call.from_user)

    products = await stoa(user.product_cart.all)()
    title = _('make_payment', user.lang)
    description = _('payment_description', user.lang).format(
        phone_number=contact_number)
    prices = await stoa(get_label_prices)(products)
    keyboard = await stoa(get_payment_buttons)(user, products)

    await call.message.delete()
    await call.message.answer(text=_('make_payment', user.lang), reply_markup=ReplyKeyboardRemove())
    await dp.bot.send_invoice(call.message.chat.id,
                              title=title,
                              description=description,
                              provider_token=PAYMENT_PROVIDER,
                              currency='UZS',
                              is_flexible=True,
                              prices=prices,
                              start_parameter='sportshop-bot-payment',
                              need_name=True,
                              need_phone_number=True,
                              need_shipping_address=True,
                              payload="invoice_for_products",
                              reply_markup=keyboard)

    await ClickPaymentState.pay_button.set()


@dp.shipping_query_handler(lambda query: True, state=ClickPaymentState.pay_button)
async def shipping(shipping_query: types.ShippingQuery):
    """When user open shipping methods"""

    user: User = await get_user(shipping_query.from_user)

    shipping_options = get_shipping_options(user)
    await bot.answer_shipping_query(shipping_query.id, ok=True, shipping_options=shipping_options)


@dp.callback_query_handler(text='cancel_payment', state=ClickPaymentState.pay_button)
async def cancel_order(call: types.CallbackQuery, state: FSMContext):
    """Cancel order when user press cancel button"""

    user: User = await get_user(call.from_user)

    await call.message.delete()
    await state.finish()
    await send_main_menu(user)


@dp.pre_checkout_query_handler(lambda query: True, state=ClickPaymentState.pay_button)
async def checkout(pre_checkout_query: types.PreCheckoutQuery):
    """Check payment query and response"""

    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    await ClickPaymentState.expect_payment.set()


def get_products_list(order):
    return order.products_list


def get_ordered_products_list(user: User):
    return [product.id for product in user.product_cart.all()]


@dp.message_handler(content_types=ContentTypes.SUCCESSFUL_PAYMENT, state=ClickPaymentState.expect_payment)
async def got_payment(message: types.Message):
    """When user has successfully transferred money for products"""

    user: User = await get_user(message.from_user)

    address = f"Davlat:  {message.successful_payment.order_info.shipping_address.country_code}\n" \
              f"Viloyat:   {message.successful_payment.order_info.shipping_address.city}\n" \
              f"Shahar:   {message.successful_payment.order_info.shipping_address.state}\n" \
              f"Manzil 1:   {message.successful_payment.order_info.shipping_address.street_line1}\n" \
              f"Manzil 2:   {message.successful_payment.order_info.shipping_address.street_line2}\n" \
              f"Pochta indeksi:  {message.successful_payment.order_info.shipping_address.post_code}\n"
    name = message.successful_payment.order_info.name
    phone_number = '+' + message.successful_payment.order_info.phone_number
    total_amount = message.successful_payment.total_amount // 100
    product_list = await stoa(get_ordered_products_list)(user)
    shipping_option = shipping_options[message.successful_payment.shipping_option_id]

    order: Order = await stoa(Order.objects.create)(user=user,
                                                    total_cost=total_amount,
                                                    address_location=address)
    await stoa(order.ordered_products.set)(product_list)

    products_set = await stoa(get_products_list)(order)

    to_group_message = f"Yangi buyurtma #{order.id}\n\n" \
                       f"<b>👤 Foydalanuvchi:</b>\n" \
                       f"  Ismi:   <a href='{user.mention_link()}'>{name}</a>\n" \
                       f"  Telefon raqami:   {phone_number}\n" \
                       f"  Turar joyi:   {shipping_option}\n\n" \
                       f"<b>📍 Manzil:</b><code>\n{address}</code>\n\n" \
                       f"<b>📦 Olingan maxsulotlar:</b>\n<code>{products_set}</code>\n\n" \
                       f"<b>📅 To'lov sanasi:</b>   {datetime.now().strftime('%d/%M/%Y, %H:%M')}\n\n" \
                       f"<b>💳 To'langan summa:</b>   {total_amount} so'm."

    try:
        await dp.bot.send_message(chat_id=int(ORDERS_GROUP), text=to_group_message)
    except Exception as error:
        logging.error(str(error))

    await stoa(user.product_cart.clear)()

    answer_message = str(_('successfully_payment_msg', user.lang)).format(phone_number=CONTACT_NUMBER,
                                                                          order_number=order.id)
    await message.answer(text=answer_message)
    await send_main_menu(user)
