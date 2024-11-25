from faststream.kafka import KafkaBroker

from app.core.config import KAFKA_BROKER, RAG_TOPIC, COUNTERS_TOPIC

kafka_producer = KafkaBroker(KAFKA_BROKER)

async def produce_rag(message: dict):
    await kafka_producer.publish(message, topic=RAG_TOPIC)


async def produce_counters(message: dict):
    await kafka_producer.publish(message, topic=COUNTERS_TOPIC)
