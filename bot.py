
import os
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from dotenv import load_dotenv
import httpx

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="✍️ Названия")],
    [KeyboardButton(text="💬 Слоганы")],
    [KeyboardButton(text="📦 Описания")],
    [KeyboardButton(text="🍷 Тост / Цитата")]
], resize_keyboard=True)

@dp.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await message.answer("Здравствуйте, мы готовы вам помочь с короткими текстами всего за полчашки кофе!", reply_markup=menu)

@dp.message(F.text.in_({"✍️ Названия", "💬 Слоганы", "📦 Описания", "🍷 Тост / Цитата"}))
async def ask_topic(message: Message, state: FSMContext):
    await state.update_data(type=message.text)
    await message.answer("Введите тематику или описание")

@dp.message()
async def generate(message: Message, state: FSMContext):
    data = await state.get_data()
    type_ = data.get("type")
    if not type_:
        await message.answer("Пожалуйста, выберите категорию с помощью меню.")
        return

    prompt = {
        "✍️ Названия": f"Придумай 5 коротких креативных названий на тему: {message.text}",
        "💬 Слоганы": f"Придумай 3 слогана или подписей на тему: {message.text}",
        "📦 Описания": f"Придумай описание товара или услуги на тему: {message.text}",
        "🍷 Тост / Цитата": f"Придумай тост или креативную цитату на тему: {message.text}",
    }.get(type_, message.text)

    try:
        response = await httpx.AsyncClient().post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/cinematika-7b",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        await message.answer(content)
    except Exception as e:
        logging.exception(e)
        await message.answer("🔹 ❌ Не удалось сгенерировать текст. Попробуйте позже.")

if __name__ == "__main__":
    dp.run_polling(bot)
