import requests, json, re, instaloader

def parse_tiktok(url):
    try:
        shortcode = re.findall(r'/@(.+)/video/(\d+)', url)[0][1]
        api_url = f"https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/aweme/detail/?aweme_id={shortcode}"
        data = requests.get(api_url, timeout=10).json()
        video = data['aweme_detail']
        return {
            "likes": video['statistics']['digg_count'],
            "views": video['statistics']['play_count'],
            "comments": [
                {"user": c['user']['unique_id'], "text": c['text']}
                for c in video.get('comments', [])[:5]
            ]
        }
    except Exception as e:
        return {"error": str(e)}

def parse_instagram(url):
    try:
        L = instaloader.Instaloader()
        shortcode = re.findall(r"/p/([a-zA-Z0-9_-]+)", url)[0]
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        return {
            "likes": post.likes,
            "comments": [
                {"user": c.owner.username, "text": c.text}
                for c in post.get_comments()[:5]
            ]
        }
    except Exception as e:
        return {"error": str(e)}
