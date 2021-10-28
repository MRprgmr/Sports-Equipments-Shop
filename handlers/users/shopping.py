from aiogram.types.callback_query import CallbackQuery
from aiogram.types.inline_keyboard import InlineKeyboardButton
from aiogram.types.input_media import InputMediaPhoto
from loader import dp
from aiogram import types
from utils.core import stoa, get_user
from aiogram.dispatcher.storage import FSMContext
from Bot.models import Category, Product, User
from utils.core import send_main_menu
from localization.strings import _
from states.private_states import CartState, ShoppingState
from filters.private_filters import text_translations_filter, category_filter
from keyboards.default.private_buttons import get_catalogs_list_template, get_back_button
from keyboards.inline.private_templates import make_cart_view_template, make_product_view_template, product_view_callback, add_to_cart


@dp.message_handler(text_translations_filter('menu_catalog_btn'), state='*')
async def catalog_button(message: types.Message):
    """When user press cataog button in main menu"""

    user: User = await get_user(message.from_user)

    text, keyboard = await stoa(get_catalogs_list_template)(user)

    await ShoppingState.catalogs.set()
    await message.answer(text=text, reply_markup=keyboard)


@dp.message_handler(text_translations_filter('back'), state=ShoppingState.catalogs)
async def back_from_catalogs(message: types.Message, state: FSMContext):
    """When user press back button in catalogs"""

    user: User = await get_user(message.from_user)

    await state.finish()
    await send_main_menu(user)


@dp.message_handler(category_filter(), state=ShoppingState.catalogs)
async def show_products(message: types.Message, state: FSMContext):
    """When any catalog selected from the list"""

    user: User = await get_user(message.from_user)
    category = await stoa(Category.objects.get)(title=message.text)

    text, keyboard, photo = await stoa(make_product_view_template)(user, category, 0)
    if text == "empty":
        await message.answer(text=_('catalog_empty', user.lang))
        return

    await message.answer(text=_('products', user.lang), reply_markup=(await stoa(get_back_button)(user)))
    await message.answer_photo(photo=photo, caption=text, reply_markup=keyboard)
    await ShoppingState.product_view.set()


@dp.message_handler(text_translations_filter('back'), state=ShoppingState.product_view)
async def back_to_catalogs(message: types.Message, state: FSMContext):
    """When user press back button during product view"""

    user: User = await get_user(message.from_user)

    text, keyboard = await stoa(get_catalogs_list_template)(user)

    await ShoppingState.catalogs.set()
    await message.answer(text=text, reply_markup=keyboard)


@dp.callback_query_handler(product_view_callback.filter(), state=ShoppingState.product_view)
async def change_product(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    """When user press left or right button from product view"""

    user: User = await get_user(call.from_user)
    category = await stoa(Category.objects.get)(id=callback_data['category_id'])

    text, keyboard, photo = await stoa(make_product_view_template)(user, category, int(callback_data['product_number']))
    await call.message.edit_media(media=types.InputMediaPhoto(media=photo))
    await call.message.edit_caption(caption=text, reply_markup=keyboard)


@dp.callback_query_handler(text='null', state=ShoppingState.product_view)
async def null_call(call: CallbackQuery):
    """Answer null call in product view"""

    await call.answer()


@dp.callback_query_handler(add_to_cart.filter(), state=ShoppingState.product_view)
async def add_product_to_cart(call: CallbackQuery, state: FSMContext, callback_data: dict):
    """Add product to cart when user press add button"""

    user: User = await get_user(call.from_user)

    keyboard = call.message.reply_markup
    keyboard.inline_keyboard[1] = [InlineKeyboardButton(
        text=_('go_to_cart_btn', user.lang), callback_data='product_cart')]

    product = await stoa(Product.objects.get)(id=int(callback_data['product_id']))
    await stoa(user.product_cart.add)(product)

    await call.message.edit_reply_markup(reply_markup=keyboard)
    await call.answer(text=_('added_to_cart_msg', user.lang))


@dp.callback_query_handler(text='product_cart', state=ShoppingState.product_view)
async def open_the_product_cart(call: CallbackQuery):
    """Open the product cart when user press open button"""

    user: User = await get_user(call.from_user)

    text, keyboard, photo = await stoa(make_cart_view_template)(user, 0)

    await call.message.edit_media(media=InputMediaPhoto(photo))
    await call.message.edit_caption(caption=text, reply_markup=keyboard)
    await CartState.opened_cart.set()
