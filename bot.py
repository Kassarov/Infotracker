#!/usr/bin/env python3
# bot.py  –  Web-Service-совместимый Telegram-бот (TikTok + Instagram профили)

import os
import asyncio
import json
import re
from aiogram import Bot, Dispatcher, types
from database_profile import init_db, get_post, save_post
from parser_profile   import get_tiktok_profile_posts, get_instagram_profile_posts
import aiohttp.web as web

# --------------- настройки -----------------
BOT_TOKEN   = os.getenv("BOT_TOKEN") or "8400432306:AAGCINBV4yA0YN-Rt9rE2WCGlCwpGW27gzo"
YOUR_ID     = int(os.getenv("YOUR_ID") or 1590094614)   # ← @userinfobot
CHECK_SEC = 60
# ------------------------------------------

bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher()

tracked_profiles = set()

# =====================  HTTP-заглушка (асинхронно)  =====================
async def health(_):
    return web.Response(text="OK")

async def start_site():
    port = int(os.getenv("PORT", 8000))
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"[INFO] Health-check server started on port {port}")

# =====================  уведомления  =====================
async def send(msg: str):
    await bot.send_message(YOUR_ID, msg)

# =====================  приём профилей  =====================
@dp.message(lambda m: m.text and m.text.startswith("http"))
async def add_profile(message: types.Message):
    url = message.text.strip()
    if "tiktok.com/@" in url or "instagram.com/" in url:
        tracked_profiles.add(url)
        await message.answer("✅ Профиль добавлен в отслеживание!")
    else:
        await message.answer("❌ Отправь ссылку на профиль TikTok или Instagram")

# =====================  фоновый монитор  =====================
async def monitor():
    await asyncio.sleep(15)
    while True:
        for profile_url in list(tracked_profiles):
            platform = "tiktok" if "tiktok.com" in profile_url else "instagram"
            posts    = []
            if platform == "tiktok":
                posts = get_tiktok_profile_posts(profile_url)
            else:
                posts = get_instagram_profile_posts(profile_url)

            for p in posts:
                old = get_post(p["post_id"])
                if not old:          # новый пост
                    await send(f"📱 {platform.upper()}\n🆕 Новый пост!\n{p['url']}")
                    save_post(p["post_id"], platform, p["url"],
                              p["likes"], p["views"], p["comments"])
                    continue

                old_likes, old_views, old_comments_json = old
                old_comments = json.loads(old_comments_json)

                # лайки
                if p["likes"] > old_likes:
                    await send(f"📱 {platform.upper()}\n❤️ +лайк на посте\n{p['url']}")

                # +1000 просмотров (только тикток)
                if platform == "tiktok" and p["views"] // 1000 > old_views // 1000:
                    await send(f"📱 TIKTOK\n👁️ +1000 просмотров на посте\n{p['url']}")

                # комментарии
                old_keys = {c["user"] + c["text"] for c in old_comments}
                for c in p["comments"]:
                    if c["user"] + c["text"] not in old_keys:
                        await send(f"📱 {platform.upper()}\n💬 Новый комментарий\n"
                                   f"👤 @{c['user']}\n💬 {c['text']}\n{p['url']}")

                save_post(p["post_id"], platform, p["url"],
                          p["likes"], p["views"], p["comments"])

        await asyncio.sleep(CHECK_SEC)

# =====================  запуск  =====================
async def main():
    init_db()
    # одновременно поднимаем HTTP-заглушку и polling
    await asyncio.gather(
        start_site(),
        monitor(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
