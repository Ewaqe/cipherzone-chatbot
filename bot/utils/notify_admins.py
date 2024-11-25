import logging

from data.config import ADMINS


async def on_startup_notify(bot):
    for admin in ADMINS:
        try:
            await bot.send_message(admin, "Bot has started")

        except Exception as err:
            logging.exception(err)
