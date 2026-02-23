
import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove, KeyboardButton

from aiogram.utils.keyboard import ReplyKeyboardBuilder

# ──────────────────────────────────────────────
TOKEN = 8645128580:AAE01cRpbAjbozxVhff6L4zf-R_xAhBPj1A          # ← замени на свой токен от BotFather
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


# ─── Главная клавиатура ──────────────────────────────────────────────────────

def get_main_keyboard() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.button(text="Подобрать корм")
    builder.button(text="Оформить заказ")

    builder.adjust(1)  # по одной кнопке в ряд; можно изменить на 2

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие..."
    )


main_kb = get_main_keyboard()


# ─── Хендлеры ────────────────────────────────────────────────────────────────

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я помогу подобрать корм для твоей собаки 🐶\n\n"
        "Нажми кнопку ниже, чтобы начать.",
        reply_markup=main_kb
    )


@dp.message(lambda m: m.text == "Подобрать корм")
async def start_form(message: types.Message, state: FSMContext):
    await state.set_state(Form.breed)
    await message.answer(
        "Какая порода у твоей собаки?",
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(Form.breed)
async def process_breed(message: types.Message, state: FSMContext):
    await state.update_data(breed=message.text.strip())
    await state.set_state(Form.age)
    await message.answer("Сколько лет / месяцев твоей собаке?")


@dp.message(Form.age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text.strip())
    await state.set_state(Form.weight)
    await message.answer("Какой вес собаки (в кг)?  Например: 12 или 4.5")


@dp.message(Form.weight)
async def process_weight(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text.strip())
    await state.set_state(Form.activity)
    await message.answer(
        "Какой уровень активности?\n\n"
        "1 — мало гуляет, диванная собака\n"
        "2 — средняя активность\n"
        "3 — очень активная, много бегает / тренировки"
    )


@dp.message(Form.activity)
async def process_activity(message: types.Message, state: FSMContext):
    await state.update_data(activity=message.text.strip())
    await state.set_state(Form.features)
    await message.answer(
        "Есть ли особенности / проблемы?\n"
        "(аллергия, стерилизация, чувствительное пищеварение, ожирение и т.д.)\n"
        "Если нет — напиши «нет»"
    )


@dp.message(Form.features)
async def process_features(message: types.Message, state: FSMContext):
    await state.update_data(features=message.text.strip())

    data = await state.get_data()

    summary = (
        f"Данные собаки:\n"
        f"• Порода: {data.get('breed', '—')}\n"
        f"• Возраст: {data.get('age', '—')}\n"
        f"• Вес: {data.get('weight', '—')} кг\n"
        f"• Активность: {data.get('activity', '—')}\n"
        f"• Особенности: {data.get('features', 'нет')}\n\n"
        f"Рекомендую рассмотреть следующие варианты:\n\n"
        f"1. Корм Ягнёнок с рисом 12 кг — 3200 ₽\n"
        f"   (универсальный, для средних и крупных пород)\n\n"
        f"2. Корм Индейка гипоаллергенный 10 кг — 3800 ₽\n"
        f"   (подходит при аллергии, чувствительном ЖКТ)\n\n"
        f"3. Корм для щенков Курица 5 кг — 1800 ₽\n"
        f"   (для щенков до 12 месяцев)\n\n"
        f"Напиши номер варианта (1, 2 или 3), который тебе подходит"
    )

    await message.answer(summary)
    await state.set_state(Form.choice)


@dp.message(Form.choice)
async def process_choice(message: types.Message, state: FSMContext):
    await state.update_data(choice=message.text.strip())
    await state.set_state(Form.quantity)
    await message.answer("Сколько упаковок хочешь заказать?")


@dp.message(Form.quantity)
async def process_quantity(message: types.Message, state: FSMContext):
    await state.update_data(quantity=message.text.strip())
    await state.set_state(Form.name)
    await message.answer("Как к тебе обращаться? (имя)")


@dp.message(Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(Form.phone)
    await message.answer("Твой номер телефона для связи")


@dp.message(Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    await state.set_state(Form.address)
    await message.answer("Адрес доставки\n(или напиши «самовывоз»)")


@dp.message(Form.address)
async def process_address_and_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()

    order_text = (
        "🛒 <b>Новый заказ!</b>\n\n"
        f"Клиент: {data.get('name', '—')}\n"
        f"Телефон: {data.get('phone', '—')}\n"
        f"Адрес: {message.text}\n\n"
        f"Порода: {data.get('breed', '—')}\n"
        f"Вес: {data.get('weight', '—')} кг\n"
        f"Выбрал вариант: {data.get('choice', '—')}\n"
        f"Количество: {data.get('quantity', '—')} шт"
    )

    try:
        await bot.send_message(ADMIN_ID, order_text, parse_mode="HTML")
        await message.answer(
            "Заказ успешно отправлен! 🎉\nСкоро с тобой свяжутся.\nСпасибо!",
            reply_markup=main_kb
        )
    except Exception as e:
        await message.answer(
            "Заказ сформирован, но не удалось отправить уведомление администратору.\n"
            "Пожалуйста, свяжись с нами напрямую.",
            reply_markup=main_kb
        )
        logging.error(f"Не удалось отправить заказ админу: {e}")

    await state.clear()


# ─── Запуск ──────────────────────────────────────────────────────────────────

async def main():
    await dp.start_polling(bot, allowed_updates=types.default_allowed_updates)


if __name__ == "__main__":
    asyncio.run(main())

