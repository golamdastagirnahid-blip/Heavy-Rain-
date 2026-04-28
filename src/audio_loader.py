"""
Audio Loader
Loads random audio from Google Drive Public Folder
Uses gdown to handle Google Drive downloads properly
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
        self._files    = []

    def _get_all_files(self):
        """
        Get all files from Google Drive folder
        using gdown folder listing
        """
        if self._files:
            return self._files

        print(
            f"   📂 Scanning folder: "
            f"{self.folder_id}"
        )

        try:
            import gdown

            # Get folder contents using gdown
            folder_url = (
                f"https://drive.google.com"
                f"/drive/folders/{self.folder_id}"
            )

            files = gdown.download_folder(
                url          = folder_url,
                skip_download= True,
                quiet        = False,
            )

            if files:
                self._files = [
                    {
                        "id"  : f.get("id", ""),
                        "name": f.get("name", "Rain Audio")
                    }
                    for f in files
                    if f.get("id")
                ]

                print(
                    f"   ✅ Found "
                    f"{len(self._files)} files"
                )
                return self._files

        except Exception as e:
            print(f"   ⚠️ gdown folder error: {e}")

        # Fallback to manual scraping
        return self._scrape_folder()

    def _scrape_folder(self):
        """
        Fallback: scrape folder page
        to find file IDs
        """
        print("   🔄 Trying folder scrape...")
        try:
            session  = requests.Session()
            headers  = {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36"
                )
            }

            # Get folder page
            url      = (
                f"https://drive.google.com"
                f"/drive/folders/{self.folder_id}"
            )
            response = session.get(
                url,
                headers = headers,
                timeout = 30
            )

            if response.status_code == 200:
                # Find file metadata in JSON
                # Google embeds file data in page
                pattern = (
                    r'\["([\w-]{28,})",'
                    r'null,null,null,null,'
                    r'"([^"]+\.'
                    r'(?:mp3|m4a|wav|ogg|flac|aac))"'
                    r'\]'
                )
                matches = re.findall(
                    pattern,
                    response.text,
                    re.IGNORECASE
                )

                if matches:
                    files = [
                        {"id": m[0], "name": m[1]}
                        for m in matches
                    ]
                    self._files = files
                    print(
                        f"   ✅ Found "
                        f"{len(files)} audio files"
                    )
                    return files

                # Try alternative pattern
                pattern2 = (
                    r'"([\w-]{28,33})",'
                    r'"([^"]+\.'
                    r'(?:mp3|m4a|wav|ogg|flac|aac))"'
                )
                matches2 = re.findall(
                    pattern2,
                    response.text,
                    re.IGNORECASE
                )

                if matches2:
                    files = [
                        {"id": m[0], "name": m[1]}
                        for m in matches2
                    ]
                    self._files = files
                    print(
                        f"   ✅ Found "
                        f"{len(files)} audio files"
                    )
                    return files

                print("   ⚠️ No audio files found in page")

        except Exception as e:
            print(f"   ⚠️ Scrape error: {e}")

        return []

    def get_total(self):
        return len(self._get_all_files())

    def download_random(self):
        """
        Pick random file and download it
        Returns (local_path, name)
        """
        files = self._get_all_files()

        if not files:
            print("   ❌ No files found in folder")
            return None, None

        # Pick random
        audio   = random.choice(files)
        file_id = audio["id"]
        name    = audio["name"]

        print(f"   🎵 Selected: {name}")

        return self._download(file_id, name)

    def _download(self, file_id, name):
        """
        Download using gdown
        Most reliable for Google Drive
        """
        local_path = os.path.join(
            AUDIO_DIR,
            f"{file_id}.m4a"
        )

        # Use cache if valid
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

        # Method 1: gdown (best for Google Drive)
        result = self._gdown(file_id, local_path)
        if result:
            return result, name

        # Method 2: requests with confirm
        result = self._requests_download(
            file_id, local_path
        )
        if result:
            return result, name

        print("   ❌ All methods failed")
        return None, None

    def _gdown(self, file_id, local_path):
        """Download using gdown library"""
        try:
            import gdown

            url = (
                f"https://drive.google.com/uc"
                f"?id={file_id}"
            )

            print("   🔄 Method 1: gdown...")
            gdown.download(
                url,
                local_path,
                quiet = False,
                fuzzy = True,
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
            print(f"   ⚠️ gdown error: {e}")
            return None

    def _requests_download(self, file_id, local_path):
        """Download using requests"""
        try:
            print("   🔄 Method 2: requests...")
            session  = requests.Session()
            headers  = {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64)"
                )
            }

            url      = (
                f"https://drive.google.com/uc"
                f"?export=download"
                f"&id={file_id}"
                f"&confirm=t"
            )
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
                print("   ⚠️ Got HTML page")
                return None

            if response.status_code == 200:
                with open(local_path, "wb") as f:
                    for chunk in response.iter_content(
                        chunk_size=32768
                    ):
                        if chunk:
                            f.write(chunk)

                size = os.path.getsize(local_path)
                if size > 1024 * 100:
                    print(
                        f"   ✅ Downloaded: "
                        f"{size // 1024 // 1024} MB"
                    )
                    return local_path

            if os.path.exists(local_path):
                os.remove(local_path)
            return None

        except Exception as e:
            print(f"   ⚠️ requests error: {e}")
            return None
