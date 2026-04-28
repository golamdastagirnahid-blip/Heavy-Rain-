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
        Handles large file confirmation automatically
        """
        local_path = os.path.join(
            AUDIO_DIR,
            f"{file_id}.m4a"
        )

        # Use cached file if already downloaded
        if os.path.exists(local_path):
            size = os.path.getsize(local_path)
            if size > 1024 * 1024:  # bigger than 1MB
                print(
                    f"   ✅ Using cached audio: "
                    f"{size // 1024 // 1024} MB"
                )
                return local_path, name
            else:
                # Delete corrupt cache
                os.remove(local_path)

        print(f"   📥 Downloading: {name}...")

        try:
            session = requests.Session()

            # Initial download request
            url      = (
                f"https://drive.google.com/uc"
                f"?export=download&id={file_id}"
            )
            response = session.get(
                url,
                stream  = True,
                timeout = 300
            )

            # Handle large file warning page
            if "download_warning" in response.text:
                token = re.search(
                    r'confirm=([^&"\']+)',
                    response.text
                )
                if token:
                    confirm_url = (
                        f"https://drive.google.com/uc"
                        f"?export=download"
                        f"&id={file_id}"
                        f"&confirm={token.group(1)}"
                    )
                    response = session.get(
                        confirm_url,
                        stream  = True,
                        timeout = 300
                    )

            # Handle cookie based confirmation
            for key, val in session.cookies.items():
                if "download_warning" in key:
                    confirm_url = (
                        f"https://drive.google.com/uc"
                        f"?export=download"
                        f"&id={file_id}"
                        f"&confirm={val}"
                    )
                    response = session.get(
                        confirm_url,
                        stream  = True,
                        timeout = 300
                    )
                    break

            if response.status_code == 200:
                with open(local_path, "wb") as f:
                    for chunk in response.iter_content(
                        chunk_size=32768
                    ):
                        if chunk:
                            f.write(chunk)

                size = os.path.getsize(local_path)

                # Verify file is valid
                if size < 1024 * 100:  # less than 100KB
                    print(
                        "   ❌ Downloaded file too small\n"
                        "   Download may have failed"
                    )
                    os.remove(local_path)
                    return None, None

                print(
                    f"   ✅ Downloaded: "
                    f"{size // 1024 // 1024} MB"
                )
                return local_path, name

            else:
                print(
                    f"   ❌ HTTP Error: "
                    f"{response.status_code}"
                )
                return None, None

        except Exception as e:
            print(f"   ❌ Download error: {e}")
            if os.path.exists(local_path):
                os.remove(local_path)
            return None, None