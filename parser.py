import re, requests, instaloader

SESSION = requests.Session()
L = instaloader.Instaloader(download_pictures=False, download_videos=False)

def parse_tiktok(url: str):
    try:
        aweme_id = re.findall(r"/video/(\d+)", url)[0]
        api = f"https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/aweme/detail/?aweme_id={aweme_id}"
        j = SESSION.get(api, timeout=10).json()["aweme_detail"]
        return {
            "likes"   : j["statistics"]["digg_count"],
            "views"   : j["statistics"]["play_count"],
            "comments": [{"user": c["user"]["unique_id"], "text": c["text"]}
                         for c in j.get("comments", [])[:10]]
        }
    except Exception as e:
        return {"error": str(e)}

def parse_instagram(url: str):
    try:
        short = re.findall(r"/p/([a-zA-Z0-9_-]+)", url)[0]
        post  = instaloader.Post.from_shortcode(L.context, short)
        return {
            "likes"   : post.likes,
            "views"   : 0,   # у постов нет публичного счётчика просмотров
            "comments": [{"user": c.owner.username, "text": c.text}
                         for c in post.get_comments()[:10]]
        }
    except Exception as e:
        return {"error": str(e)}
