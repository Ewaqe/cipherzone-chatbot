import asyncio

from loader import dp, bot
from kafka.consumer import kafka_consumer
from kafka.producer import kafka_producer
from utils.notify_admins import on_startup_notify

import middlewares, filters, handlers


async def on_startup(dispatcher):
    await kafka_consumer.start()
    await kafka_producer.start()
    await on_startup_notify(bot)


async def on_shutdown(dispatcher):
    await kafka_consumer.stop()
    await kafka_producer.stop()


async def main():
    await bot.delete_webhook(drop_pending_updates=True)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(main())
