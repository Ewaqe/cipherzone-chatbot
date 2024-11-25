from aiogram import types
from aiogram.filters.command import CommandStart

from data import user_sessions
from loader import dp


@dp.message(CommandStart())
async def bot_start(message: types.Message):
    await message.answer("Привет! Я - твой личный ассистент.\nЯ буду консультировать тебя по различным вопросам в социальных сферах, а также умею выполнить некоторые функции.")
