import asyncio
import logging

from aiogram.dispatcher.filters.builtin import Command
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import ContentTypes as ct
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types.message import Message
from aiogram.types.reply_keyboard import ReplyKeyboardRemove
from asgiref.sync import sync_to_async

from Bot.models import User
from filters.private_filters import IsAdmin
from loader import dp


# show admin commands --------------------------------------------
@dp.message_handler(IsAdmin(), Command('commands'), state="*")
async def show_admin_commands(message: Message):
    answer = "\n".join([
        "Admin commands:\n",
        "/broadcast — send broadcast to bot users.",
    ])
    await message.answer(answer)


# -----------------------------------------------------------------
# broadcast ---------------------------------------------------------
cancel_button = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1,
                                    keyboard=[
                                        [
                                            KeyboardButton(
                                                text="❌ Cancel broadcast"),
                                        ],
                                    ])


class BroadCastState(StatesGroup):
    start = State()


def get_users():
    users = User.objects.all()
    result = []
    for usr in users:
        result.append(usr.user_id)
    return result


@dp.message_handler(IsAdmin(), Command('broadcast'), state="*")
async def send_broadcast(message: Message):
    await message.answer("Send a message to be broadcast:", reply_markup=cancel_button)
    await BroadCastState.start.set()


@dp.message_handler(IsAdmin(), text="❌ Cancel broadcast", state=BroadCastState.start)
async def cancel(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("Canceled.", reply_markup=ReplyKeyboardRemove())


@dp.message_handler(IsAdmin(), content_types=ct.TEXT | ct.AUDIO | ct.PHOTO | ct.VIDEO | ct.VIDEO_NOTE | ct.LOCATION,
                    state=BroadCastState.start)
async def send_broadcast_start(message: Message, state: FSMContext):
    await message.answer("Broadcast started...")
    users_ids = await sync_to_async(get_users)()
    count = 0
    try:
        for user_id in users_ids:
            try:
                await message.send_copy(user_id)
                count += 1
            except Exception as error:
                logging.info(str(error))
        await asyncio.sleep(.01)
    finally:
        await message.answer(f"Message sent to {count} users.", reply_markup=ReplyKeyboardRemove())
    await state.finish()
# ------------------------------------------------------------------------
