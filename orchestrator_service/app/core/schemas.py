from pydantic import BaseModel


class UserSchema(BaseModel):
    telegram_id: int
    first_name: str | None
    last_name: str | None
    username: str | None
    language_code: str = 'ru'

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    'telegram_id': 1,
                    'first_name': 'asdasdasd',
                    'last_name': None,
                    'username': 'minecrafterkirill',
                    'language_code': 'ru'
                }
            ]
        }
    }


class RequestSchema(BaseModel):
    user: UserSchema
    query: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user": UserSchema(telegram_id=1, 
                                              first_name='asdasdasd',
                                              last_name=None,
                                              username='minecrafterkirill',
                                              language_code='ru'),
                    "query": "Как вызвать врача?",
                }
            ]
        }
    }
