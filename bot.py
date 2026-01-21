import asyncio, json, re
from aiogram import Bot, Dispatcher, types
from database import init_db, get_last_data, set_last_data
from parser import parse_tiktok, parse_instagram

BOT_TOKEN = "8400432306:AAFg0b3sUA-bODsf4Ddbym8OcbW4eWOpzU8"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(lambda msg: msg.text and msg.text.startswith("http"))
async def handle_link(message: types.Message):
    url = message.text.strip()
    platform = None
    if "tiktok.com" in url:
        platform = "tiktok"
        data = parse_tiktok(url)
    elif "instagram.com" in url:
        platform = "instagram"
        data = parse_instagram(url)
    else:
        await message.reply("❌ Поддерживаются только TikTok и Instagram.")
        return

    if "error" in data:
        await message.reply(f"❌ Ошибка парсинга: {data['error']}")
        return

    last = get_last_data(url)
    last_data = json.loads(last) if last else {}
    set_last_data(url, platform, json.dumps(data))

    # Просто ответим первым данным
    text = f"✅ Отслеживаю!\nЛайков: {data['likes']}\nКомментариев: {len(data['comments'])}"
    await message.reply(text)

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
