from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.reply_keyboard import ReplyKeyboardRemove
from Bot.models import User
from keyboards.inline.private_templates import make_orders_view_template, orders_button
from loader import dp
from localization.strings import _
from filters.private_filters import text_translations_filter
from states.private_states import OrdersState
from utils.core import get_user, send_main_menu, stoa


@dp.message_handler(text_translations_filter('menu_orders_btn'), state='*')
async def list_orders(message: types.Message):
    """Show user orders"""
    
    user: User = await get_user(message.from_user)
    text, keyboard = await stoa(make_orders_view_template)(user, 0)

    if text == 'empty':
        await message.answer(text=_('no_orders', user.lang))
        return
    
    await message.answer(_('my_orders', user.lang), reply_markup=ReplyKeyboardRemove())
    await message.answer(text=text, reply_markup=keyboard)
    await OrdersState.order_view.set()


@dp.callback_query_handler(text='null', state=OrdersState.order_view)
async def null_request(call: CallbackQuery):
    await call.answer()


@dp.callback_query_handler(text='back', state=OrdersState.order_view)
async def go_back(call: types.CallbackQuery, state: FSMContext):
    """Go to main menu from orders"""

    user: User = await get_user(call.from_user)

    await call.message.delete()
    await state.finish()
    await send_main_menu(user)


@dp.callback_query_handler(orders_button.filter(), state=OrdersState.order_view)
async def change_order(call: types.CallbackQuery, callback_data: dict):
    """Change order when left or right button pressed"""

    user: User = await get_user(call.from_user)

    text, keyboard = await stoa(make_orders_view_template)(user, int(callback_data['order_id']))
    await call.message.edit_text(text=text, reply_markup=keyboard)