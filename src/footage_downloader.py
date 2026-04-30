"""
Stock Footage Downloader
Downloads rain footage from Pexels + Pixabay
Selects 1 clip and loops for full video
"""

import os
import random
import requests


FOOTAGE_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ),
    "downloads", "footage"
)

os.makedirs(FOOTAGE_DIR, exist_ok=True)

KEYWORDS = [
    "heavy rain",
    "rain storm",
    "rain window",
    "rain nature",
    "thunder rain",
    "rain forest",
    "rain night",
    "rain drops",
    "rainfall",
    "stormy rain",
]


class FootageDownloader:

    def __init__(self):
        self.pexels_key  = os.getenv(
            "PEXELS_API_KEY",  ""
        )
        self.pixabay_key = os.getenv(
            "PIXABAY_API_KEY", ""
        )

    def get_footage(self):
        """
        Get rain footage clip
        Tries Pexels first then Pixabay
        """
        print("   🎬 Getting stock footage...")
        keyword = random.choice(KEYWORDS)
        print(f"   🔍 Keyword: {keyword}")

        if self.pexels_key:
            result = self._pexels(keyword)
            if result:
                return result

        if self.pixabay_key:
            result = self._pixabay(keyword)
            if result:
                return result

        print("   ❌ No footage found")
        return None

    def _pexels(self, keyword):
        """Download from Pexels"""
        try:
            print("   📡 Trying Pexels...")
            headers  = {
                "Authorization": self.pexels_key
            }
            params   = {
                "query"      : keyword,
                "per_page"   : 15,
                "orientation": "landscape",
                "size"       : "large",
            }
            response = requests.get(
                "https://api.pexels.com"
                "/videos/search",
                headers = headers,
                params  = params,
                timeout = 30
            )

            if response.status_code != 200:
                return None

            videos = response.json().get(
                "videos", []
            )
            if not videos:
                return None

            video    = random.choice(videos)
            video_id = video["id"]
            files    = sorted(
                video.get("video_files", []),
                key=lambda x: x.get("width", 0),
                reverse=True
            )

            url = None
            for f in files:
                if f.get("width", 0) >= 1280:
                    url = f["link"]
                    break
            if not url and files:
                url = files[0]["link"]

            if not url:
                return None

            local = os.path.join(
                FOOTAGE_DIR,
                f"pexels_{video_id}.mp4"
            )
            return self._dl(url, local, "Pexels")

        except Exception as e:
            print(f"   ⚠️ Pexels: {e}")
            return None

    def _pixabay(self, keyword):
        """Download from Pixabay"""
        try:
            print("   📡 Trying Pixabay...")
            params   = {
                "key"       : self.pixabay_key,
                "q"         : keyword,
                "video_type": "film",
                "per_page"  : 15,
                "order"     : "popular",
            }
            response = requests.get(
                "https://pixabay.com/api/videos/",
                params  = params,
                timeout = 30
            )

            if response.status_code != 200:
                return None

            hits = response.json().get("hits", [])
            if not hits:
                return None

            video    = random.choice(hits)
            video_id = video["id"]
            videos   = video.get("videos", {})

            url = None
            for q in ["large", "medium", "small"]:
                if q in videos:
                    url = videos[q].get("url")
                    if url:
                        break

            if not url:
                return None

            local = os.path.join(
                FOOTAGE_DIR,
                f"pixabay_{video_id}.mp4"
            )
            return self._dl(url, local, "Pixabay")

        except Exception as e:
            print(f"   ⚠️ Pixabay: {e}")
            return None

    def _dl(self, url, local_path, source):
        """Download video file"""
        try:
            if os.path.exists(local_path):
                size = os.path.getsize(local_path)
                if size > 1024 * 1024:
                    print(
                        f"   ✅ Cached: "
                        f"{size // 1024 // 1024} MB"
                    )
                    return local_path

            print(
                f"   ⬇️ Downloading "
                f"from {source}..."
            )
            response = requests.get(
                url,
                stream  = True,
                timeout = 120
            )

            if response.status_code == 200:
                with open(local_path, "wb") as f:
                    for chunk in response.iter_content(
                        chunk_size=32768
                    ):
                        if chunk:
                            f.write(chunk)

                size = os.path.getsize(local_path)
                print(
                    f"   ✅ Footage: "
                    f"{size // 1024 // 1024} MB"
                )
                return local_path

            return None

        except Exception as e:
            print(f"   ❌ DL error: {e}")
            return None
