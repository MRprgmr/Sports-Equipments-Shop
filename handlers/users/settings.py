from aiogram import types
from aiogram.dispatcher.storage import FSMContext

from Bot.models import User
from filters.private_filters import text_translations_filter
from keyboards.default.private_buttons import get_user_settings_template, languages_selection_template, \
    get_contact_send_template
from loader import dp
from localization.strings import check_language_by_text, _
from states.private_states import SettingsState
from utils.core import send_main_menu
from utils.core import stoa, get_user, phone_number_validater


@dp.message_handler(text_translations_filter('menu_settings_btn'), state='*')
async def user_settings(message: types.Message):
    """When user press settings button in main menu"""

    user: User = await get_user(message.from_user)

    text, keyboard = await stoa(get_user_settings_template)(user)
    await message.answer(text=text, reply_markup=keyboard)
    await SettingsState.options.set()


@dp.message_handler(text_translations_filter('back'), state=SettingsState.options)
async def back_to_main_menu(message: types.Message, state: FSMContext):
    """Back button pressed inside settings menu"""

    user: User = await get_user(message.from_user)

    await state.finish()
    await send_main_menu(user)


@dp.message_handler(text_translations_filter('change_language_btn'), state=SettingsState.options)
async def user_language_change(message: types.Message, state: FSMContext):
    """When user press change language in settings menu"""

    user: User = await get_user(message.from_user)

    text, keyboard = await stoa(languages_selection_template)()
    await SettingsState.change_language.set()
    await message.answer(text=text, reply_markup=keyboard)


@dp.message_handler(text_translations_filter('language_my'), state=SettingsState.change_language)
async def get_selected_language(message: types.Message, state: FSMContext):
    """When user selected any language from the given list"""
    user: User = await get_user(message.from_user)
    language_code = await stoa(check_language_by_text)('language_my', message.text)
    user.lang = language_code
    await stoa(user.save)()
    await message.answer(text=_('language_set', user.lang))
    await state.finish()
    await send_main_menu(user)


@dp.message_handler(text_translations_filter('change_number_btn'), state=SettingsState.options)
async def change_number_selected(message: types.Message, state: FSMContext):
    """When user press change phone number button inside settings menu"""

    user: User = await get_user(message.from_user)

    text, keyboard = await stoa(get_contact_send_template)(user.lang)
    text = _('current_number_msg', user.lang).format(
        number=user.contact) + "\n\n" + text

    await message.answer(text=text, reply_markup=keyboard)
    await SettingsState.change_number.set()


@dp.message_handler(state=SettingsState.change_number, content_types=['text', 'contact'])
async def check_and_enter_phone_number(message: types.Message, state: FSMContext):
    """When user send contact or phone number in a text form"""

    user: User = await get_user(message.from_user)

    phone_number = await phone_number_validater(message)

    if phone_number is not None:
        user.contact = phone_number
        await stoa(user.save)()

        await message.answer(text=_('number_changed_msg', user.lang).format(number=phone_number))
        await send_main_menu(user)

        await state.finish()
    else:
        await message.answer(text=_('incorrect_format_number', user.lang))
