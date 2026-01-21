import asyncio, json, os, re
from aiogram import Bot, Dispatcher, types
from database_profile import init_db, get_post, save_post
from parser_profile import get_tiktok_profile_posts, get_instagram_profile_posts

BOT_TOKEN   = os.getenv("BOT_TOKEN") or "8400432306:AAFg0b3sUA-bODsf4Ddbym8OcbW4eWOpzU8"
YOUR_ID     = int(os.getenv("YOUR_ID") or 1590094614)   # ← @userinfobot


bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher()

CHECK_SEC = 5*60
tracked_profiles = set()

async def send(msg: str):
    await bot.send_message(YOUR_ID, msg)

# ------- приём ссылки на профиль -------
@dp.message(lambda m: m.text and m.text.startswith("http"))
async def add_profile(message: types.Message):
    url = message.text.strip()
    if "tiktok.com/@" in url or "instagram.com/" in url:
        tracked_profiles.add(url)
        await message.answer("✅ Профиль добавлен в отслеживание!")
    else:
        await message.answer("❌ Отправь ссылку на профиль TikTok или Instagram")

# ------- фоновый монитор -------
async def monitor():
    await asyncio.sleep(15)
    while True:
        for profile_url in list(tracked_profiles):
            platform = "tiktok" if "tiktok.com" in profile_url else "instagram"
            posts = []
            if platform == "tiktok":
                posts = get_tiktok_profile_posts(profile_url)
            else:
                posts = get_instagram_profile_posts(profile_url)

            for p in posts:
                old = get_post(p["post_id"])
                if not old:
                    # новый пост
                    await send(f"📱 {platform.upper()}\n🆕 Новый пост!\n{p['url']}")
                    save_post(p["post_id"], platform, p["url"], p["likes"], p["views"], p["comments"])
                    continue

                old_likes, old_views, old_comments_json = old
                old_comments = json.loads(old_comments_json)

                # лайки
                if p["likes"] > old_likes:
                    await send(f"📱 {platform.upper()}\n❤️ +1 лайк на посте\n{p['url']}")

                # +1000 просмотров (только тикток)
                if platform == "tiktok" and p["views"]//1000 > old_views//1000:
                    await send(f"📱 TIKTOK\n👁️ +1000 просмотров на посте\n{p['url']}")

                # комментарии
                old_keys = {c["user"]+c["text"] for c in old_comments}
                for c in p["comments"]:
                    if c["user"]+c["text"] not in old_keys:
                        await send(f"📱 {platform.upper()}\n💬 Новый комментарий под постом\n{p['url']}\n👤 @{c['user']}\n💬 {c['text']}")

                save_post(p["post_id"], platform, p["url"], p["likes"], p["views"], p["comments"])

        await asyncio.sleep(CHECK_SEC)

# ------- запуск -------
async def main():
    init_db()
    asyncio.create_task(monitor())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
