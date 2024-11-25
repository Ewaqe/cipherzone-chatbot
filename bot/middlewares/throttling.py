from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
import time


class Throttled(Exception):
    def __init__(self, key, rate, delta, exceeded_count):
        self.key = key
        self.rate = rate
        self.delta = delta
        self.exceeded_count = exceeded_count

    def __str__(self):
        return f"Rate limit exceeded! (Limit: {self.rate}s, Delta: {self.delta}s, Exceeded Count: {self.exceeded_count})"
    

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit: float = 0.5, key_prefix: str = 'antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        self.throttle_data = {} 
        super(ThrottlingMiddleware, self).__init__()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        try:
            await self.on_process_event(event, data)
        except CancelHandler:
            return 

        return await handler(event, data)

    async def on_process_event(self, event: Message, data: dict) -> None:
        limit = getattr(data["handler"].callback, "throttling_rate_limit", self.rate_limit)
        key = getattr(data["handler"].callback, "throttling_key", f"{self.prefix}_message")

        full_key = f"{key}_{event.from_user.id}_{event.chat.id}"

        now = time.time()
        last_call = self.throttle_data.get(full_key, {}).get("last_call", 0)
        delta = now - last_call

        if delta < limit:
            throttled = Throttled(
                key=key,
                rate=limit,
                delta=delta,
                exceeded_count=self.throttle_data.get(full_key, {}).get("exceeded_count", 0) + 1
            )
            await self.event_throttled(event, throttled)
            raise CancelHandler()

        self.throttle_data[full_key] = {
            "last_call": now,
            "exceeded_count": 0
        }

    async def event_throttled(self, event: Message, throttled: Throttled):
        delta = throttled.rate - throttled.delta
        if throttled.exceeded_count <= 2:
            await event.answer(f"Слишком много запросов. Попробуйте через {round(delta)} секунд.")


class CancelHandler(Exception):
    ...
