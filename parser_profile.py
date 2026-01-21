import re, requests, instaloader

L = instaloader.Instaloader(download_pictures=False, download_videos=False)
SESSION = requests.Session()

def get_tiktok_profile_posts(profile_url: str):
    """
    Возвращает список постов профиля TikTok:
    [{post_id, url, likes, views, comments:[{user,text}]}]
    """
    try:
        username = re.findall(r"@(\w+)", profile_url)[0]
        api = f"https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/aweme/post/?sec_user_id=&count=20&max_cursor=0&aid=1180&user_id={username}"
        j = SESSION.get(api, timeout=10).json()
        posts = []
        for aw in j.get("aweme_list", []):
            posts.append({
                "post_id": aw["aweme_id"],
                "url": f"https://www.tiktok.com/@{username}/video/{aw['aweme_id']}",
                "likes": aw["statistics"]["digg_count"],
                "views": aw["statistics"]["play_count"],
                "comments": [
                    {"user": c["user"]["unique_id"], "text": c["text"]}
                    for c in aw.get("comments", [])[:10]
                ]
            })
        return posts
    except Exception as e:
        print("TikTok profile error:", e)
        return []

def get_instagram_profile_posts(profile_url: str):
    # временно отключаем Instagram
    print("[WARN] Instagram temporarily disabled (401)")
    return []
