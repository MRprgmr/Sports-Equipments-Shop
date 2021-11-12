from typing import List, Tuple

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from Bot.models import User, Category
from localization.strings import get_all_languages, _


def get_back_button(user: User):
    back_button = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_('back', user.lang))]
        ],
        resize_keyboard=True
    )

    return back_button


def languages_selection_template() -> Tuple[str, List[List]]:
    """Return text and keyboard of available languages"""

    languages = get_all_languages()
    languages_title = [_("language", lang_id) for lang_id in languages]

    text = f"🈯️  <b>{' | '.join(languages_title)}</b>\n\n"
    text += "\n——————————————\n".join([_('language_choose', lang_id)
                                       for lang_id in languages])

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(_(f'language_my', lang_id))
             for lang_id in languages],
        ],
        resize_keyboard=True,
    )
    return text, keyboard


def get_contact_send_template(lang):
    """Return contact send text and button"""

    text = _('request_contact', lang)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_('request_contact_btn', lang),
                               request_contact=True),
            ]
        ],
        resize_keyboard=True,
    )
    return text, keyboard


def get_main_menu_template(lang):
    """Return main menu text and keyboard for specific language"""

    text = _('main_menu', lang)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_('menu_catalog_btn', lang)),
                KeyboardButton(text=_('cart_btn', lang)),
            ],
            [
                KeyboardButton(text=_('menu_orders_btn', lang)),
                KeyboardButton(text=_('menu_settings_btn', lang)),
            ],
            [
                KeyboardButton(text=_('menu_posts_btn', lang)),
                KeyboardButton(text=_('menu_help_btn', lang)),
            ]
        ],
        resize_keyboard=True,
    )
    return text, keyboard


def get_user_settings_template(user: User):
    """Return keyboard and text when user press settings button"""

    text = _('settings', user.lang)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_('change_language_btn', user.lang)),
                KeyboardButton(text=_('change_number_btn', user.lang))
            ],
            [
                KeyboardButton(text=_('back', user.lang))
            ]
        ],
        resize_keyboard=True,
    )
    return text, keyboard


def get_catalogs_list_template(user: User):
    """Return available categories keyboard and text"""

    text = _('choose_category', user.lang)

    keyboard_list = []
    categories = Category.objects.filter(status=True)

    if categories.count() & 1:
        end = categories.count() - 1
    else:
        end = categories.count()

    for i in range(0, end, 2):
        keyboard_list.append(
            [
                KeyboardButton(text=categories[i].title),
                KeyboardButton(text=categories[i + 1].title)
            ]
        )
    if categories.count() & 1:
        keyboard_list.append(
            [
                KeyboardButton(text=categories.last().title)
            ]
        )
    keyboard_list.append(
        [KeyboardButton(text=_('back', user.lang))]
    )

    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_list,
        resize_keyboard=True,
        row_width=2
    )

    return text, keyboard
