"""
Audio Loader
Loads random audio from Google Drive Public Folder
Uses file IDs from audio_list.json
"""

import os
import re
import json
import random
import requests


AUDIO_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ),
    "downloads", "audio"
)

os.makedirs(AUDIO_DIR, exist_ok=True)

AUDIO_LIST_FILE = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ),
    "audio_list.json"
)


class AudioLoader:

    def __init__(self):
        with open(AUDIO_LIST_FILE, "r") as f:
            data = json.load(f)
        self.folder_id = data.get("folder_id", "")
        self.files     = data.get("files", [])

    def get_total(self):
        return len(self.files)

    def download_random(self):
        """
        Pick a random audio file and download it
        Returns (local_path, name)
        """
        if not self.files:
            print("   ❌ No files in audio_list.json")
            return None, None

        # Pick random file
        audio   = random.choice(self.files)
        file_id = audio["id"]
        name    = audio["name"]

        print(f"   🎵 Selected: {name}")

        return self._download(file_id, name)

    def _download(self, file_id, name):
        """
        Download file from Google Drive
        Tries multiple methods
        """
        local_path = os.path.join(
            AUDIO_DIR,
            f"{file_id}.m4a"
        )

        # Use cached file if already downloaded
        if os.path.exists(local_path):
            size = os.path.getsize(local_path)
            if size > 1024 * 1024:
                print(
                    f"   ✅ Using cached: "
                    f"{size // 1024 // 1024} MB"
                )
                return local_path, name
            else:
                os.remove(local_path)

        print(f"   📥 Downloading: {name}...")

        # Try all methods
        for method_num, method in enumerate([
            self._method1,
            self._method2,
            self._method3,
        ], 1):
            print(f"   🔄 Method {method_num}...")
            result = method(file_id, local_path)
            if result:
                return result, name

        print("   ❌ All download methods failed")
        return None, None

    def _method1(self, file_id, local_path):
        """Method 1: gdown library"""
        try:
            import gdown
            url = (
                f"https://drive.google.com/uc"
                f"?id={file_id}"
            )
            gdown.download(
                url,
                local_path,
                quiet=False,
                fuzzy=True
            )
            if os.path.exists(local_path):
                size = os.path.getsize(local_path)
                if size > 1024 * 100:
                    print(
                        f"   ✅ Downloaded: "
                        f"{size // 1024 // 1024} MB"
                    )
                    return local_path
            return None
        except Exception as e:
            print(f"   ⚠️ Method 1 error: {e}")
            return None

    def _method2(self, file_id, local_path):
        """Method 2: requests with confirm token"""
        try:
            session  = requests.Session()
            url      = (
                f"https://drive.google.com/uc"
                f"?export=download&id={file_id}&confirm=t"
            )
            headers  = {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64)"
                )
            }
            response = session.get(
                url,
                headers = headers,
                stream  = True,
                timeout = 300
            )

            content_type = response.headers.get(
                "Content-Type", ""
            )
            if "text/html" in content_type:
                return None

            return self._save(response, local_path)

        except Exception as e:
            print(f"   ⚠️ Method 2 error: {e}")
            return None

    def _method3(self, file_id, local_path):
        """Method 3: Direct download link"""
        try:
            session  = requests.Session()
            url      = (
                f"https://drive.google.com"
                f"/uc?export=download"
                f"&id={file_id}"
                f"&confirm=t"
                f"&uuid=1"
            )
            headers  = {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(X11; Linux x86_64)"
                ),
                "Accept": "*/*",
            }
            response = session.get(
                url,
                headers         = headers,
                stream          = True,
                timeout         = 300,
                allow_redirects = True
            )

            content_type = response.headers.get(
                "Content-Type", ""
            )
            if "text/html" in content_type:
                return None

            return self._save(response, local_path)

        except Exception as e:
            print(f"   ⚠️ Method 3 error: {e}")
            return None

    def _save(self, response, local_path):
        """Save response to file and verify"""
        try:
            if response.status_code != 200:
                return None

            with open(local_path, "wb") as f:
                for chunk in response.iter_content(
                    chunk_size=32768
                ):
                    if chunk:
                        f.write(chunk)

            size = os.path.getsize(local_path)

            if size < 1024 * 100:
                if os.path.exists(local_path):
                    os.remove(local_path)
                return None

            print(
                f"   ✅ Downloaded: "
                f"{size // 1024 // 1024} MB"
            )
            return local_path

        except Exception as e:
            print(f"   ⚠️ Save error: {e}")
            if os.path.exists(local_path):
                os.remove(local_path)
            return None
