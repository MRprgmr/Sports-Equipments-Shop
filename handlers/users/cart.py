from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.types.input_media import InputMediaPhoto

from Bot.models import Product
from Bot.models import User
from filters.private_filters import text_translations_filter
from keyboards.default.private_buttons import get_back_button
from keyboards.inline.private_templates import make_cart_view_template, product_in_cart, remove_from_cart
from loader import dp
from localization.strings import _
from states.private_states import CartState
from utils.core import get_user, send_main_menu, stoa


@dp.message_handler(text_translations_filter('cart_btn'), state='*')
async def open_my_cart(message: types.Message):
    """When user press open cart button"""

    user: User = await get_user(message.from_user)

    text, keyboard, photo = await stoa(make_cart_view_template)(user, 0)

    if text == "empty":
        await message.answer(text=_('cart_is_empty', user.lang))
        return

    await message.answer(text=_('products_in_cart', user.lang), reply_markup=(await stoa(get_back_button)(user)))
    await message.answer_photo(photo=photo, caption=text, reply_markup=keyboard)
    await CartState.opened_cart.set()


@dp.message_handler(text_translations_filter('back'), state=CartState.opened_cart)
async def back_from_cart(message: types.Message, state: FSMContext):
    """When user press back button in opened cart"""

    user: User = await get_user(message.from_user)

    await state.finish()
    await send_main_menu(user)


@dp.callback_query_handler(product_in_cart.filter(), state=CartState.opened_cart)
async def change_product(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    """When user press left or right button in opened cart"""

    user: User = await get_user(call.from_user)

    text, keyboard, photo = await stoa(make_cart_view_template)(user, int(callback_data['product_id']))
    await call.message.edit_media(media=types.InputMediaPhoto(media=photo))
    await call.message.edit_caption(caption=text, reply_markup=keyboard)


@dp.callback_query_handler(text='null', state=CartState.opened_cart)
async def null_call(call: types.CallbackQuery):
    """Answer null call in opened cart"""

    await call.answer()


@dp.callback_query_handler(remove_from_cart.filter(), state=CartState.opened_cart)
async def remove_product_from_cart(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    """When user press delete button in opened cart"""

    user: User = await get_user(call.from_user)

    product = await stoa(Product.objects.get)(id=int(callback_data['product_id']))
    await stoa(user.product_cart.remove)(product)

    await call.answer(_('product_deleted_from_cart', user.lang))

    current_id = int(callback_data['current_number'])
    if current_id:
        current_id -= 1

    text, keyboard, photo = await stoa(make_cart_view_template)(user, current_id)

    if text == "empty":
        await call.message.delete()
        await call.message.answer(text=_('cart_is_empty', user.lang))
        await state.finish()
        await send_main_menu(user)
        return

    await call.message.edit_media(media=InputMediaPhoto(photo))
    await call.message.edit_caption(caption=text, reply_markup=keyboard)
