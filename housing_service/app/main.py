from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.kafka.consumer import kafka_consumer
from app.kafka.producer import kafka_producer

app = FastAPI()

app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    await kafka_producer.start()
    await kafka_consumer.start()


@app.on_event("shutdown")
async def shutdown_event():
    await kafka_producer.stop()
    await kafka_consumer.stop()
