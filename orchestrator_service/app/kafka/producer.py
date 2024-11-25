from faststream.kafka import KafkaBroker

from app.core.config import KAFKA_BROKER, REQUESTS_TOPIC, RAG_TOPIC

kafka_producer = KafkaBroker(KAFKA_BROKER, enable_idempotence=True)

async def produce_request(message: dict):
    await kafka_producer.publish(message, topic=REQUESTS_TOPIC)


async def produce_rag(message: dict):
    await kafka_producer.publish(message, topic=RAG_TOPIC)
