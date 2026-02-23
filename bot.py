import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# ──────────────────────────────────────────────
TOKEN = "8645128580:AAE01cRpbAjbozxVhff6L4zf-R_xAhBPj1A"          # ← замени на свой токен от BotFather
ADMIN_ID = 462740408                 # ← твой Telegram ID (узнай через @userinfobot)
# ──────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class Form(StatesGroup):
    breed = State()
    age = State()
    weight = State()
    activity = State()
    features = State()
    choice = State()
    quantity = State()
    name = State()
    phone = State()
    address = State()

from aiogram.utils.keyboard import ReplyKeyboardBuilder

# ... (остальной код)

builder = ReplyKeyboardBuilder()

builder.button(text="Подобрать корм")
builder.button(text="Оформить заказ")

builder.adjust(1)  # по 1 кнопке в ряд (можно 2, если хочешь в одну строку)

main_kb = builder.as_markup(
    resize_keyboard=True,
    one_time_keyboard=False
)

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "Привет! Я помогу подобрать корм для твоей собаки 🐶\n\n"
        "Нажми кнопку ниже, чтобы начать.",
        reply_markup=main_kb
    )

@dp.message(lambda m: m.text == "Подобрать корм")
async def start_form(message: types.Message, state: FSMContext):
    await state.set_state(Form.breed)
    await message.answer("Порода собаки?", reply_markup=ReplyKeyboardRemove())

@dp.message(Form.breed)
async def process_breed(message: types.Message, state: FSMContext):
    await state.update_data(breed=message.text)
    await state.set_state(Form.age)
    await message.answer("Возраст (в годах или месяцах для щенков)?")

@dp.message(Form.age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(Form.weight)
    await message.answer("Вес собаки (кг)?")

@dp.message(Form.weight)
async def process_weight(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await state.set_state(Form.activity)
    await message.answer("Уровень активности?\n1 — мало гуляет\n2 — средний\n3 — очень активная")

@dp.message(Form.activity)
async def process_activity(message: types.Message, state: FSMContext):
    await state.update_data(activity=message.text)
    await state.set_state(Form.features)
    await message.answer("Особенности? (аллергия, стерилизация, чувствительное пищеварение и т.д. — или «нет»)")

@dp.message(Form.features)
async def process_features(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(features=message.text)

    summary = (
        f"Подбор для:\n"
        f"Порода: {data['breed']}\n"
        f"Возраст: {data['age']}\n"
        f"Вес: {data['weight']} кг\n"
        f"Активность: {data['activity']}\n"
        f"Особенности: {data.get('features', 'нет')}\n\n"
        "Рекомендую:\n"
        "1. Корм Ягнёнок с рисом 12 кг — 3200 ₽ (для средних пород)\n"
        "2. Корм Индейка гипоаллергенный 10 кг — 3800 ₽\n"
        "3. Корм для щенков Курица 5 кг — 1800 ₽\n\n"
        "Напиши номер варианта (1, 2 или 3), который хочешь заказать"
    )
    await message.answer(summary)
    await state.set_state(Form.choice)

@dp.message(Form.choice)
async def process_choice(message: types.Message, state: FSMContext):
    await state.update_data(choice=message.text)
    await state.set_state(Form.quantity)
    await message.answer("Сколько упаковок?")

@dp.message(Form.quantity)
async def process_quantity(message: types.Message, state: FSMContext):
    await state.update_data(quantity=message.text)
    await state.set_state(Form.name)
    await message.answer("Как к тебе обращаться?")

@dp.message(Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Form.phone)
    await message.answer("Номер телефона?")

@dp.message(Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(Form.address)
    await message.answer("Адрес доставки (или «самовывоз»)?")
    
@dp.message(Form.address)
async def process_address(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order = (
        f"🛒 Новый заказ!\n\n"
        f"Клиент: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Адрес: {message.text}\n\n"
        f"Порода: {data['breed']}\n"
        f"Вес: {data['weight']} кг\n"
        f"Выбрал: вариант {data['choice']}\n"
        f"Количество: {data['quantity']} шт"
    )
    await bot.send_message(ADMIN_ID, order)
    await message.answer("Заказ отправлен! Скоро с тобой свяжутся 🐕 Спасибо!")
    await state.clear()
    await message.answer("Хочешь подобрать ещё?", reply_markup=main_kb)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())
