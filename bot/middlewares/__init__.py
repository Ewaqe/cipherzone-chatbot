from loader import dp
from .throttling import ThrottlingMiddleware


if __name__ == "middlewares":
    dp.message.middleware(ThrottlingMiddleware(limit=1.0))
