import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder
from faststream.kafka import KafkaBroker

from loader import bot
from data import user_sessions
from data.config import KAFKA_BROKER, COUNTERS_TOPIC
from handlers.users.query import handle_next_pair, prompt_for_counters

kafka_consumer = KafkaBroker(KAFKA_BROKER)


@kafka_consumer.subscriber(COUNTERS_TOPIC)
async def consume_message(message: dict):
    """Обрабатывает сообщения из Kafka."""
    pairs = message.get("pairs")
    user_id = message.get("telegram_id")
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    
    if pairs is not None: 
        if pairs:
            user_sessions[user_id]["pairs"] = pairs
            await handle_next_pair(user_id)
        else: 
            await prompt_for_counters(user_id)
    else:  # If pairs is None
        await prompt_for_counters(user_id)



