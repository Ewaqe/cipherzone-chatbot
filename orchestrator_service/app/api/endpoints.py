import asyncio
from fastapi import APIRouter
from sqlalchemy import select

from app.core.database import use_session
from shared.models import *
from app.core.logging import logger
from app.core.schemas import RequestSchema
from app.llm.workflows import PreprocessFlow
from app.kafka.producer import produce_request

router = APIRouter()

@router.post("/send")
async def send_message(request: RequestSchema):
    asyncio.create_task(preprocess_task(request))
    return {"status": "message sent"}


@router.post("/process_message")
async def process_pairs():
    tg_id = 1663095778
    pairs = [
        {'name': 'Холодная вода', 'value': 150},
        {'name': 'Электричество', 'value': 131}
    ]
    await produce_request({'pairs': pairs, 'telegram_id': tg_id})
    return {"status": "message sent"}


@router.post("/process_empty_message")
async def process_no_pairs():
    tg_id = 1663095778
    await produce_request({'pairs': None, 'telegram_id': tg_id})
    return {"status": "message sent"}


async def preprocess_task(request):
    preprocessor = PreprocessFlow()
    topic = await preprocessor.run(query=request.query)

    async with use_session() as session:
        statement = select(User).filter_by(telegram_id=request.user.telegram_id)
        user = await session.scalar(statement)
        if user is None:
            user = User(telegram_id=request.user.telegram_id, first_name=request.user.first_name,
                        last_name=request.user.last_name, username=request.user.username, language_code=request.user.language_code)
            session.add(user)
            await session.commit()

        new_request = Request(user_id=user.id, query=request.query, topic=topic)
        session.add(new_request)
        await session.commit()

    request_dict = {
        'id': new_request.id,
        'user_id': new_request.user_id,
        'telegram_id': user.telegram_id,
        'query': new_request.query,
        'topic': new_request.topic
    }
    logger.info(f'Отправляю запрос: {request_dict}')
    await produce_request({'request': request_dict})
