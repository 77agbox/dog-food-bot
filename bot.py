import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# ──────────────────────────────────────────────
TOKEN = "8645128580:AAE01cRpbAjbozxVhff6L4zf-R_xAhBPj1A"
ADMIN_ID = 462740408
# ──────────────────────────────────────────────

# Настраиваем логирование — чтобы видеть, что происходит
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

print("=== bot.py начал выполняться ===")
sys.stdout.flush()

try:
    bot = Bot(token=TOKEN)
    logger.info("Бот успешно создан")
except Exception as e:
    logger.error(f"Ошибка при создании Bot: {e}")
    print(f"Критическая ошибка при создании Bot: {e}")
    sys.exit(1)

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
    builder.adjust(1)  # по одной кнопке в столбик
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие…"
    )


main_kb = get_main_keyboard()


# ─── Хендлеры ────────────────────────────────────────────────────────────────

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я помогу подобрать корм для твоей собаки 🐶\n\n"
        "Нажми кнопку ниже, чтобы начать подбор.",
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
    await message.answer("Сколько лет или месяцев твоей собаке?")


@dp.message(Form.age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text.strip())
    await state.set_state(Form.weight)
    await message.answer("Какой вес собаки в кг? (можно дробное число)")


@dp.message(Form.weight)
async def process_weight(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text.strip())
    await state.set_state(Form.activity)
    await message.answer(
        "Уровень активности:\n\n"
        "1 — мало гуляет\n"
        "2 — средняя активность\n"
        "3 — очень активная"
    )


@dp.message(Form.activity)
async def process_activity(message: types.Message, state: FSMContext):
    await state.update_data(activity=message.text.strip())
    await state.set_state(Form.features)
    await message.answer(
        "Есть ли особенности? (аллергия, стерилизация, чувствительное пищеварение, ожирение и т.д.)\n"
        "Если нет — напиши «нет»"
    )


@dp.message(Form.features)
async def process_features(message: types.Message, state: FSMContext):
    await state.update_data(features=message.text.strip())

    data = await state.get_data()

    text = (
        "Твоя собака:\n"
        f"• Порода: {data.get('breed', '—')}\n"
        f"• Возраст: {data.get('age', '—')}\n"
        f"• Вес: {data.get('weight', '—')} кг\n"
        f"• Активность: {data.get('activity', '—')}\n"
        f"• Особенности: {data.get('features', 'нет')}\n\n"
        "Рекомендую рассмотреть:\n\n"
        "1. Ягнёнок с рисом 12 кг — 3200 ₽\n"
        "2. Индейка гипоаллергенный 10 кг — 3800 ₽\n"
        "3. Для щенков курица 5 кг — 1800 ₽\n\n"
        "Напиши номер (1, 2 или 3)"
    )

    await message.answer(text)
    await state.set_state(Form.choice)


@dp.message(Form.choice)
async def process_choice(message: types.Message, state: FSMContext):
    await state.update_data(choice=message.text.strip())
    await state.set_state(Form.quantity)
    await message.answer("Сколько упаковок?")


@dp.message(Form.quantity)
async def process_quantity(message: types.Message, state: FSMContext):
    await state.update_data(quantity=message.text.strip())
    await state.set_state(Form.name)
    await message.answer("Как тебя зовут?")


@dp.message(Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(Form.phone)
    await message.answer("Номер телефона для связи")


@dp.message(Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    await state.set_state(Form.address)
    await message.answer("Адрес доставки (или напиши «самовывоз»)")


@dp.message(Form.address)
async def process_address_and_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()

    order = (
        "🛒 <b>Новый заказ</b>\n\n"
        f"Клиент: {data.get('name', '—')}\n"
        f"Телефон: {data.get('phone', '—')}\n"
        f"Адрес: {message.text}\n\n"
        f"Порода: {data.get('breed', '—')}\n"
        f"Вес: {data.get('weight', '—')} кг\n"
        f"Вариант: {data.get('choice', '—')}\n"
        f"Количество: {data.get('quantity', '—')} шт"
    )

    try:
        await bot.send_message(ADMIN_ID, order, parse_mode="HTML")
        await message.answer(
            "Заказ отправлен! 🎉 Скоро с тобой свяжутся.\nСпасибо!",
            reply_markup=main_kb
        )
    except Exception as e:
        logger.error(f"Не удалось отправить заказ админу: {e}")
        await message.answer(
            "Заказ сформирован, но уведомление не отправилось.\n"
            "Пожалуйста, свяжись с нами напрямую.",
            reply_markup=main_kb
        )

    await state.clear()


# ─── Запуск ──────────────────────────────────────────────────────────────────

async def main():
    logger.info("Запуск бота начат")

    try:
        me = await bot.get_me()
        logger.info(f"Успешная авторизация → @{me.username} ({me.first_name})")
        print(f"Бот запущен как: @{me.username}")
        sys.stdout.flush()
    except Exception as e:
        logger.error(f"Ошибка авторизации: {e}")
        print(f"Ошибка авторизации: {e}")
        sys.stdout.flush()
        return

    # Удаляем webhook, если он был установлен ранее
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook удалён (если был)")
    except Exception:
        pass

    logger.info("Запускаем polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка в main: {e}")
