from faststream.kafka import KafkaBroker

from app.kafka.producer import produce_rag
from app.core.config import KAFKA_BROKER, REQUESTS_TOPIC

kafka_consumer = KafkaBroker(KAFKA_BROKER)

@kafka_consumer.subscriber(REQUESTS_TOPIC)
async def consume_requests(message: dict):
    topics = ['TRANSPORT', 'EDUCATION', 'HEALTHCARE', 'IRRELEVANT']
    if message['request']['topic'] in topics:
        await produce_rag(message)
