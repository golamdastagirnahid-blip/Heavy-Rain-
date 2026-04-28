"""
Audio Loader
Loads random audio from Google Drive Public Folder
No API keys or credentials needed
Folder ID: 17pFi9WZWW8hiwM6-DpmTjJbXEvoYHt0w
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
        Scrapes public Google Drive folder
        to get all file IDs automatically
        No API key needed
        """
        if self._files:
            return self._files

        print(
            f"   📂 Scanning folder: "
            f"{self.folder_id}"
        )

        try:
            url = (
                f"https://drive.google.com"
                f"/drive/folders/{self.folder_id}"
            )
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }

            response = requests.get(
                url,
                headers = headers,
                timeout = 30
            )

            if response.status_code == 200:
                # Find all Google Drive file IDs
                # They are exactly 33 characters
                matches = re.findall(
                    r'"([\w-]{33})"',
                    response.text
                )

                # Remove folder ID from results
                files = list(set([
                    m for m in matches
                    if m != self.folder_id
                ]))

                if files:
                    self._files = [
                        {
                            "id"  : f,
                            "name": f"Rain_Audio_{i+1}"
                        }
                        for i, f in enumerate(files)
                    ]
                    print(
                        f"   ✅ Found "
                        f"{len(self._files)} "
                        f"audio files"
                    )
                    return self._files
                else:
                    print(
                        "   ⚠️ No files found "
                        "in folder"
                    )

        except Exception as e:
            print(f"   ⚠️ Folder scan error: {e}")

        return []

    def get_total(self):
        """Return total number of audio files"""
        return len(self._get_all_files())

    def download_random(self):
        """
        Pick a random audio file and download it
        Returns (local_path, name)
        """
        files = self._get_all_files()

        if not files:
            print(
                "   ❌ No audio files found\n"
                "   Make sure folder is public"
            )
            return None, None

        # Pick random file
        audio   = random.choice(files)
        file_id = audio["id"]
        name    = audio["name"]

        print(f"   🎵 Selected: {name}")

        return self._download(file_id, name)

    def _download(self, file_id, name):
        """
        Download file from Google Drive
        Handles all Google Drive download methods
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

        # Try all download methods
        result = self._method1(file_id, local_path)
        if result:
            return result, name

        result = self._method2(file_id, local_path)
        if result:
            return result, name

        result = self._method3(file_id, local_path)
        if result:
            return result, name

        print("   ❌ All download methods failed")
        return None, None

    def _method1(self, file_id, local_path):
        """
        Method 1: Direct download with
        confirmation token from HTML
        """
        print("   🔄 Method 1: Direct download...")
        try:
            session = requests.Session()
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64)"
                )
            }

            # Step 1: Get download page
            url      = (
                f"https://drive.google.com/uc"
                f"?export=download&id={file_id}"
            )
            response = session.get(
                url,
                headers = headers,
                timeout = 60
            )

            # Step 2: Find confirm token
            token = None

            # Check in URL params
            if "confirm=" in response.url:
                token = re.search(
                    r'confirm=([^&]+)',
                    response.url
                )
                if token:
                    token = token.group(1)

            # Check in HTML
            if not token:
                token = re.search(
                    r'confirm=([^&"\']+)',
                    response.text
                )
                if token:
                    token = token.group(1)

            # Check in cookies
            if not token:
                for k, v in session.cookies.items():
                    if "download_warning" in k:
                        token = v
                        break

            # Step 3: Download with token
            if token:
                download_url = (
                    f"https://drive.google.com/uc"
                    f"?export=download"
                    f"&id={file_id}"
                    f"&confirm={token}"
                )
            else:
                download_url = url

            response = session.get(
                download_url,
                headers = headers,
                stream  = True,
                timeout = 300
            )

            return self._save_file(
                response, local_path
            )

        except Exception as e:
            print(f"   ⚠️ Method 1 failed: {e}")
            return None

    def _method2(self, file_id, local_path):
        """
        Method 2: Use export=download
        with UUID confirmation
        """
        print("   🔄 Method 2: UUID confirmation...")
        try:
            session  = requests.Session()
            headers  = {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Macintosh; Intel Mac OS X 10_15_7)"
                )
            }

            # Get the file info page first
            info_url = (
                f"https://drive.google.com"
                f"/file/d/{file_id}/view"
            )
            session.get(
                info_url,
                headers = headers,
                timeout = 30
            )

            # Now try download
            download_url = (
                f"https://drive.google.com/uc"
                f"?export=download"
                f"&id={file_id}"
                f"&confirm=t"
            )
            response = session.get(
                download_url,
                headers = headers,
                stream  = True,
                timeout = 300
            )

            return self._save_file(
                response, local_path
            )

        except Exception as e:
            print(f"   ⚠️ Method 2 failed: {e}")
            return None

    def _method3(self, file_id, local_path):
        """
        Method 3: Use drive API endpoint
        """
        print("   🔄 Method 3: API endpoint...")
        try:
            session  = requests.Session()
            headers  = {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(X11; Linux x86_64)"
                )
            }

            url      = (
                f"https://drive.google.com"
                f"/uc?id={file_id}&export=download"
                f"&authuser=0&confirm=t"
            )
            response = session.get(
                url,
                headers = headers,
                stream  = True,
                timeout = 300,
                allow_redirects = True
            )

            return self._save_file(
                response, local_path
            )

        except Exception as e:
            print(f"   ⚠️ Method 3 failed: {e}")
            return None

    def _save_file(self, response, local_path):
        """
        Save downloaded file and verify size
        """
        try:
            if response.status_code != 200:
                print(
                    f"   ⚠️ HTTP: "
                    f"{response.status_code}"
                )
                return None

            # Check content type
            content_type = response.headers.get(
                "Content-Type", ""
            )

            # If HTML returned = not the real file
            if "text/html" in content_type:
                print(
                    "   ⚠️ Got HTML instead of file"
                )
                return None

            # Save file
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(
                    chunk_size=32768
                ):
                    if chunk:
                        f.write(chunk)

            size = os.path.getsize(local_path)

            if size < 1024 * 100:  # less than 100KB
                print(
                    f"   ⚠️ File too small: "
                    f"{size} bytes"
                )
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
