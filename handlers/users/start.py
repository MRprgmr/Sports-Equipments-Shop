from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.storage import FSMContext
from aiogram.types.message import Message, ReplyKeyboardRemove

from Bot.models import User
from filters.private_filters import full_name_filter, text_translations_filter
from keyboards.default.private_buttons import get_contact_send_template, languages_selection_template
from loader import dp
from localization.strings import _, check_language_by_text
from states.private_states import RegistrationState
from utils.core import get_user, phone_number_validater, send_main_menu, stoa


@dp.message_handler(CommandStart(), state='*')
async def bot_start(message: types.Message):
    """When user send command /start"""
    user: User = await get_user(message.from_user)
    if not user.lang and not user.is_registered:
        text, keyboard = await stoa(languages_selection_template)()
    elif not user.is_registered and not user.contact:
        text, keyboard = await stoa(get_contact_send_template)(user.lang)
        await RegistrationState.phone_number.set()
    elif not user.is_registered and not user.full_name:
        text = _('request_fullname_msg', user.lang)
        keyboard = ReplyKeyboardRemove()
        await RegistrationState.full_name.set()
    else:
        await send_main_menu(user)
        return

    await message.answer(text=text, reply_markup=keyboard)


@dp.message_handler(text_translations_filter('language_my'))
async def change_language(message: Message):
    """When user select any type of language"""

    user: User = await get_user(message.from_user)
    if not user.lang and not user.is_registered:
        language_code = await stoa(check_language_by_text)('language_my', message.text)

        user.lang = language_code
        await stoa(user.save)()

        text, keyboard = await stoa(get_contact_send_template)(user.lang)
        await message.answer(text=text, reply_markup=keyboard)
        await RegistrationState.phone_number.set()


@dp.message_handler(state=RegistrationState.phone_number, content_types=['text', 'contact'])
async def input_phone_number(message: Message):
    """When user send contact or phone number"""

    user: User = await get_user(message.from_user)

    phone_number = await phone_number_validater(message)

    if phone_number is not None:
        user.contact = phone_number
        await stoa(user.save)()
        await message.answer(text=_('request_fullname_msg', user.lang), reply_markup=ReplyKeyboardRemove())
        await RegistrationState.full_name.set()
    else:
        await message.answer(text=_('incorrect_format_number', user.lang))


@dp.message_handler(full_name_filter(), state=RegistrationState.full_name)
async def input_full_name(message: Message, state: FSMContext):
    """Get user full name"""

    user: User = await get_user(message.from_user)

    user.full_name = message.text
    user.is_registered = True
    await stoa(user.save)()
    await state.finish()
    await send_main_menu(user)
