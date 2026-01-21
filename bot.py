import asyncio, json, os
from aiogram import Bot, Dispatcher, types
from database import init_db, get_last_data, set_last_data
from parser      import parse_tiktok, parse_instagram

BOT_TOKEN   = os.getenv("BOT_TOKEN") or "8400432306:AAFg0b3sUA-bODsf4Ddbym8OcbW4eWOpzU8"
YOUR_ID     = int(os.getenv("YOUR_ID") or 1590094614)   # ← @userinfobot

bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher()

CHECK_SEC = 5*60          # 5 мин
tracked   = set()         # {url, ...}

async def send(msg: str):
    await bot.send_message(YOUR_ID, msg)

# ------- приём ссылок -------
@dp.message(lambda m: m.text and m.text.startswith("http"))
async def add_url(message: types.Message):
    url = message.text.strip()
    if "tiktok.com" in url:
        plat, data = "tiktok",    parse_tiktok(url)
    elif "instagram.com" in url:
        plat, data = "instagram", parse_instagram(url)
    else:
        return await message.answer("❌ Принимаю только TikTok / Instagram")

    if "error" in data:
        return await message.answer(f"❌ Парсинг: {data['error']}")

    tracked.add(url)
    set_last_data(url, plat, json.dumps(data))
    await message.answer(
        f"✅ Отслеживаю {plat}\n"
        f"Лайков: {data['likes']}\n"
        f"Просмотров: {data.get('views','—')}\n"
        f"Комментариев: {len(data['comments'])}"
    )

# ------- фоновый монитор -------
async def monitor():
    await asyncio.sleep(15)
    while True:
        for url in list(tracked):
            plat = "tiktok" if "tiktok.com" in url else "instagram"
            old  = json.loads(get_last_data(url) or "{}")
            new  = parse_tiktok(url) if plat=="tiktok" else parse_instagram(url)
            if "error" in new:
                continue

            # лайки
            if new["likes"] > old.get("likes",0):
                await send(f"❤️ +1 лайк на {plat} ({new['likes']})")

            # +1000 просмотров (только тикток)
            if plat=="tiktok":
                if new["views"]//1000 > old.get("views",0)//1000:
                    await send(f"👁️ +1000 просмотров на TikTok ({new['views']})")

            # комментарии
            old_keys = {c["user"]+c["text"] for c in old.get("comments",[])}
            for c in new["comments"]:
                if c["user"]+c["text"] not in old_keys:
                    await send(f"💬 @{c['user']} на {plat}:\n{c['text']}")

            set_last_data(url, plat, json.dumps(new))
        await asyncio.sleep(CHECK_SEC)

# ------- запуск -------
async def main():
    init_db()
    asyncio.create_task(monitor())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
