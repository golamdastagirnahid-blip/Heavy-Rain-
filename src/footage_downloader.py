"""
Stock Footage Downloader
Downloads rain footage from Pexels and Pixabay
Selects 1 clip and loops it for the full video
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

# Search keywords for rain footage
SEARCH_KEYWORDS = [
    "heavy rain",
    "rain storm",
    "rain window",
    "rain nature",
    "thunder rain",
    "rain forest",
    "rain night",
    "rain drops",
]


class FootageDownloader:

    def __init__(self):
        self.pexels_key  = os.getenv("PEXELS_API_KEY",  "")
        self.pixabay_key = os.getenv("PIXABAY_API_KEY", "")

    def get_footage(self):
        """
        Get a rain footage clip
        Tries Pexels first, then Pixabay
        Returns local file path
        """
        print("   🎬 Getting stock footage...")

        keyword = random.choice(SEARCH_KEYWORDS)
        print(f"   🔍 Searching: {keyword}")

        # Try Pexels first
        if self.pexels_key:
            result = self._from_pexels(keyword)
            if result:
                return result

        # Try Pixabay as fallback
        if self.pixabay_key:
            result = self._from_pixabay(keyword)
            if result:
                return result

        print("   ❌ No footage found")
        return None

    def _from_pexels(self, keyword):
        """Download footage from Pexels"""
        try:
            print("   📡 Trying Pexels...")
            headers = {
                "Authorization": self.pexels_key
            }
            params = {
                "query"       : keyword,
                "per_page"    : 15,
                "orientation" : "landscape",
                "size"        : "large",
            }
            response = requests.get(
                "https://api.pexels.com/videos/search",
                headers = headers,
                params  = params,
                timeout = 30
            )

            if response.status_code != 200:
                print(
                    f"   ⚠️ Pexels: "
                    f"HTTP {response.status_code}"
                )
                return None

            data   = response.json()
            videos = data.get("videos", [])

            if not videos:
                print("   ⚠️ Pexels: No videos found")
                return None

            # Pick random video
            video   = random.choice(videos)
            video_id = video["id"]

            # Get best quality file
            files = video.get("video_files", [])
            files = sorted(
                files,
                key=lambda x: x.get("width", 0),
                reverse=True
            )

            # Pick highest quality
            video_file = None
            for f in files:
                if f.get("width", 0) >= 1920:
                    video_file = f
                    break

            if not video_file and files:
                video_file = files[0]

            if not video_file:
                return None

            url        = video_file["link"]
            local_path = os.path.join(
                FOOTAGE_DIR,
                f"pexels_{video_id}.mp4"
            )

            return self._download_file(
                url, local_path, "Pexels"
            )

        except Exception as e:
            print(f"   ⚠️ Pexels error: {e}")
            return None

    def _from_pixabay(self, keyword):
        """Download footage from Pixabay"""
        try:
            print("   📡 Trying Pixabay...")
            params = {
                "key"         : self.pixabay_key,
                "q"           : keyword,
                "video_type"  : "film",
                "per_page"    : 15,
                "order"       : "popular",
            }
            response = requests.get(
                "https://pixabay.com/api/videos/",
                params  = params,
                timeout = 30
            )

            if response.status_code != 200:
                print(
                    f"   ⚠️ Pixabay: "
                    f"HTTP {response.status_code}"
                )
                return None

            data = response.json()
            hits = data.get("hits", [])

            if not hits:
                print("   ⚠️ Pixabay: No videos found")
                return None

            # Pick random video
            video    = random.choice(hits)
            video_id = video["id"]
            videos   = video.get("videos", {})

            # Try qualities in order
            url = None
            for quality in ["large", "medium", "small"]:
                if quality in videos:
                    url = videos[quality].get("url")
                    if url:
                        break

            if not url:
                return None

            local_path = os.path.join(
                FOOTAGE_DIR,
                f"pixabay_{video_id}.mp4"
            )

            return self._download_file(
                url, local_path, "Pixabay"
            )

        except Exception as e:
            print(f"   ⚠️ Pixabay error: {e}")
            return None

    def _download_file(self, url, local_path, source):
        """Download video file from URL"""
        try:
            if os.path.exists(local_path):
                size = os.path.getsize(local_path)
                if size > 1024 * 1024:
                    print(
                        f"   ✅ Cached footage: "
                        f"{size // 1024 // 1024} MB"
                    )
                    return local_path

            print(f"   ⬇️ Downloading from {source}...")
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
                    f"   ✅ Footage downloaded: "
                    f"{size // 1024 // 1024} MB"
                )
                return local_path

            print(
                f"   ❌ HTTP {response.status_code}"
            )
            return None

        except Exception as e:
            print(f"   ❌ Download failed: {e}")
            return None