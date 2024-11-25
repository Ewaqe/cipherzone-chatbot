import logging
from urllib.parse import urljoin
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import ClientSession
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from loader import dp, bot
from data import user_sessions
from data.config import BASE_URL


class CounterStates(StatesGroup):
    WAITING_FOR_VALUE = State()
    EDITING_TYPE = State()
    EDITING_VALUE = State()


@dp.message()
async def message(message: Message, state: FSMContext):
    user = message.from_user
    current_state = await state.get_state()
    
    if current_state in [CounterStates.WAITING_FOR_VALUE.state, CounterStates.EDITING_VALUE.state]:
        value = message.text
        session_data = await state.get_data()
        
        if current_state == CounterStates.EDITING_VALUE.state:
            # Handle editing
            current_pair = user_sessions[user.id]["current_pair"]
            current_pair["value"] = value
            
            # Send updated pair to Kafka (implement your kafka sender here)
            # await send_to_kafka(topic_request, key=str(user.id), value={"counter": current_pair})
            
            await handle_next_pair(user.id)
            await state.clear()
        else:
            # Handle new counter input
            counter_type = session_data.get("selected_counter")
            builder = InlineKeyboardBuilder()
            builder.button(text="Ввести еще один счетчик", callback_data="another")
            builder.button(text="Завершить", callback_data="finish")
            
            # Send to Kafka (implement your kafka sender here)
            # await send_to_kafka(topic_request, key=str(user.id), 
            #                    value={"counter": counter_type, "value": value})
            
            await message.answer(
                f"Значение {value} для счётчика {counter_type} сохранено.",
                reply_markup=builder.as_markup()
            )
            await state.clear()
    else:
        user_schema = {
            'telegram_id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'language_code': user.language_code
        }

        data = {
            'user': user_schema,
            'query': message.text
        }

        await message.answer('Пожалуйста, подождите. Ваш запрос обрабатывается...')

        async with ClientSession() as session:
            async with session.post(
                url=urljoin(BASE_URL, '/api/orchestrator/send'),
                json=data
            ) as response:
                logging.info(await response.text())


async def handle_next_pair(user_id: int):
    """Обрабатывает следующую пару счётчиков для пользователя."""
    session = user_sessions.get(user_id, {})
    pairs = session.get("pairs", [])
    
    if not pairs:
        await bot.send_message(user_id, "Операция выполнена успешно!")
        if "current_pair" in session:
            del session["current_pair"]
        return

    current_pair = pairs.pop(0)
    session["current_pair"] = current_pair
    counter_name = current_pair["name"]
    value = current_pair["value"]

    builder = InlineKeyboardBuilder()
    builder.button(text="Подтвердить", callback_data="confirm")
    builder.button(text="Изменить", callback_data="edit")
    builder.adjust(2)

    await bot.send_message(
        user_id,
        f"Вы уверены, что хотите записать значение {value} для счётчика {counter_name}?",
        reply_markup=builder.as_markup()
    )


async def prompt_for_counters(user_id: int, state: FSMContext = None, edit_mode: bool = False):
    """Выводит пользователю список типов счётчиков для выбора."""
    counter_types = ["Электричество", "Вода", "Газ"]

    builder = InlineKeyboardBuilder()
    for counter in counter_types:
        callback_data = f"edit_type:{counter}" if edit_mode else f"counter_type:{counter}"
        builder.button(text=counter, callback_data=callback_data)
    builder.adjust(1)

    if edit_mode:
        builder.button(text="Оставить текущий тип", callback_data="keep_type")
        builder.adjust(1)

    await bot.send_message(
        user_id,
        "Выберите тип счётчика:",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(lambda c: c.data.startswith("counter_type:"))
async def handle_counter_selection(callback_query: CallbackQuery, state: FSMContext):
    counter_type = callback_query.data.split(":")[1]
    await state.update_data(selected_counter=counter_type)
    await state.set_state(CounterStates.WAITING_FOR_VALUE)
    await bot.send_message(
        callback_query.from_user.id,
        f"Введите значение для счётчика {counter_type}:"
    )
    await callback_query.answer()


@dp.callback_query(lambda c: c.data.startswith("edit_type:"))
async def handle_edit_type_selection(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик выбора нового типа счетчика при редактировании."""
    new_type = callback_query.data.split(":")[1]
    user_id = callback_query.from_user.id
    current_pair = user_sessions[user_id]["current_pair"]
    
    current_pair["name"] = new_type
    
    await state.set_state(CounterStates.EDITING_VALUE)
    await bot.send_message(
        user_id,
        f"Введите новое значение для счётчика {new_type}:"
    )
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == "keep_type")
async def handle_keep_type(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик решения оставить текущий тип счетчика."""
    user_id = callback_query.from_user.id
    current_pair = user_sessions[user_id]["current_pair"]
    
    await state.set_state(CounterStates.EDITING_VALUE)
    await bot.send_message(
        user_id,
        f"Введите новое значение для счётчика {current_pair['name']}:"
    )
    await callback_query.answer()


@dp.callback_query(lambda c: c.data in ["another", "finish"])
async def handle_finish(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data == "another":
        await prompt_for_counters(callback_query.from_user.id)
    else:
        await bot.send_message(
            callback_query.from_user.id,
            "Операция успешно завершена!"
        )
    await callback_query.answer()


@dp.callback_query(lambda c: c.data in ["confirm", "edit"])
async def handle_pair_action(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    session = user_sessions[user_id]
    current_pair = session["current_pair"]

    if callback_query.data == "confirm":
        # Handle confirming
        
        # Send to Kafka (implement your kafka sender here)
        # await send_to_kafka(topic_request, key=str(user_id),
        #                    value={"confirmed_pair": current_pair})
        
        await bot.send_message(
            user_id,
            f"Значение {current_pair['value']} для счётчика {current_pair['name']} подтверждено."
        )
        await handle_next_pair(user_id)
    
    elif callback_query.data == "edit":
        await state.set_state(CounterStates.EDITING_TYPE)
        await prompt_for_counters(user_id, state, edit_mode=True)
    
    await callback_query.answer()
