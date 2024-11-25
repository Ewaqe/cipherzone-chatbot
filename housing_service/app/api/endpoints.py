from fastapi import APIRouter

router = APIRouter()

@router.post("/send")
async def send_message(data: dict):
    return {"status": "message sent"}
