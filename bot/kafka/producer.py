from faststream.kafka import KafkaBroker

from data.config import KAFKA_BROKER, COUNTERS_TOPIC

kafka_producer = KafkaBroker(KAFKA_BROKER, enable_idempotence=True)

async def produce_message(message: dict):
    await kafka_producer.publish(message, topic=COUNTERS_TOPIC)
