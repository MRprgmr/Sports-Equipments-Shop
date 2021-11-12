from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

from Bot.models import Category
from data.config import ADMINS
from localization.strings import get_translations_from_key
from utils.core import stoa


class text_translations_filter(BoundFilter):

    def __init__(self, key: str):
        self.key = key

    async def check(self, message: Message):
        if message.text in (await stoa(get_translations_from_key)(self.key)):
            return True
        else:
            return False


class full_name_filter(BoundFilter):
    async def check(self, message: Message):

        async def is_valid(text):
            for ch in text:
                if ch.isalpha() or ch == "'":
                    continue
                else:
                    return False
            return True

        fullname = message.text.split()
        if len(fullname) == 2 and (await is_valid(fullname[0])) and (await is_valid(fullname[1])):
            return True
        else:
            return False


def get_categories():
    categories = Category.objects.all()
    return [category.title for category in categories]


class category_filter(BoundFilter):
    async def check(self, message: Message):
        titles = await stoa(get_categories)()
        if message.text in titles:
            return True
        else:
            return False


class IsAdmin(BoundFilter):
    async def check(self, message: Message):
        if str(message.from_user.id) in ADMINS:
            return True
        else:
            return False
