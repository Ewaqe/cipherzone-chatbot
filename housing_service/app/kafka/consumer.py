from faststream.kafka import KafkaBroker

from app.llm.workflows import IntentClassifier, CountersExtractor
from app.kafka.producer import produce_rag, produce_counters
from app.core.config import KAFKA_BROKER, REQUESTS_TOPIC
from app.core.logging import logger

kafka_consumer = KafkaBroker(KAFKA_BROKER)

@kafka_consumer.subscriber(REQUESTS_TOPIC)
async def consume_request(message: dict):
    logger.info(f'New message: {message}')
    if message['request']['topic'] != 'HOUSING':
        return

    intent_classifier = IntentClassifier()
    intent = await intent_classifier.run(query=message['request']['query'])
    
    logger.info(f'Предсказанный intent: {intent}')
    message['request']['intent'] = intent
    # TODO: сделать запись интента в базу данных

    if intent == 'CONSULTATION':
        await produce_rag(message)
    elif intent == 'INPUT_COUNTERS':
        counters_extractor = CountersExtractor()
        counters = await counters_extractor.run(query=message['request']['query'])
        counters['telegram_id'] = message['request']['telegram_id']
        
        logger.info(f'Counters: {counters}')
        await produce_counters(counters)
    elif intent == 'OUTPUT_COUNTERS':
        pass
        
