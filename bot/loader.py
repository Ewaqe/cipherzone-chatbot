from aiogram import Bot, Dispatcher, enums
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from data import config

storage = MemoryStorage()
bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=enums.ParseMode.HTML))
dp = Dispatcher(storage=storage)
