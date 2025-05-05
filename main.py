
import os
import logging
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

@dp.message()
async def handle_text(message: Message):
    await message.answer("⏳ Генерирую текст…")
    prompt = message.text

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://snappytext.fly.dev",
        }
        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "user", "content": f"Придумай креативный текст по теме: {prompt}"}
            ]
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            if r.status_code == 200:
                content = r.json()['choices'][0]['message']['content']
                await message.answer(content.strip())
            else:
                await message.answer("❌ Не удалось сгенерировать текст. Попробуйте позже.")

    except Exception as e:
        logging.exception(e)
        await message.answer("❌ Произошла ошибка.")

if __name__ == "__main__":
    dp.run_polling(bot)
