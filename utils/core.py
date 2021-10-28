import re
from aiogram.types.message import Message
from asgiref.sync import sync_to_async
from Bot.models import User
from loader import dp
from keyboards.default.private_buttons import get_main_menu_template
from .currency import usd_in_uzs


def stoa(x): return sync_to_async(x)


async def get_user(bot_user) -> User:
    user_data = dict(user_id=bot_user.id,
                     first_name=bot_user.first_name,
                     username=bot_user.username)
    user = await stoa((await stoa(User.objects.filter)(**user_data)).first)()
    if not user:
        user = await stoa(User.objects.create)(**user_data)
    return user


async def phone_number_validater(message: Message) -> str:
    if message.content_type == 'contact':
        phone_number = message.contact.phone_number
    else:
        phone_number = message.text
    if phone_number[0] != '+':
        phone_number = '+' + phone_number

    if re.match(r"\+998(?:33|93|94|97|90|91|98|99|95|88)\d\d\d\d\d\d\d", phone_number) is not None:
        return phone_number
    else:
        return None


async def send_main_menu(user: User):
    text, keyboard = await stoa(get_main_menu_template)(user.lang)
    await dp.bot.send_message(chat_id=user.user_id, text=text, reply_markup=keyboard)


def calculate_total_cost(products):
    """Calculate all products' total cost in user cart"""
    total = 0
    for product in products:
        if product.currency == '$':
            total += product.price*usd_in_uzs
        else:
            total += product.price
    
    return '{:,}'.format(total).replace(',', ' ') + " UZS"