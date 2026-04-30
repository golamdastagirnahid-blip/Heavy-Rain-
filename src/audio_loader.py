"""
Audio Loader
Loads random audio from Google Drive
Public Folder using gdown
"""

import os
import re
import io
import sys
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
        self.folder_id = data.get(
            "folder_id", ""
        )
        self._files = []

    def _get_all_files(self):
        """
        Get all files from Google Drive
        public folder using gdown
        """
        if self._files:
            return self._files

        print(
            f"   📂 Scanning folder: "
            f"{self.folder_id}"
        )

        try:
            import gdown

            folder_url = (
                f"https://drive.google.com"
                f"/drive/folders/{self.folder_id}"
            )

            # Capture gdown output
            old_out = sys.stdout
            old_err = sys.stderr
            sys.stdout = buf = io.StringIO()
            sys.stderr = buf

            try:
                files = gdown.download_folder(
                    url           = folder_url,
                    skip_download = True,
                    quiet         = False,
                )
            except Exception:
                files = None
            finally:
                sys.stdout = old_out
                sys.stderr = old_err

            output = buf.getvalue()

            # Parse file IDs from output
            pattern = r'Processing file ([\w-]+) (.+)'
            matches = re.findall(pattern, output)

            if matches:
                result = [
                    {
                        "id"  : m[0].strip(),
                        "name": m[1].strip()
                    }
                    for m in matches
                ]
                self._files = result
                print(
                    f"   ✅ Found "
                    f"{len(result)} files"
                )
                return result

            # Try parsing file objects
            if files:
                result = []
                for f in files:
                    try:
                        if hasattr(f, 'id'):
                            result.append({
                                "id": str(f.id),
                                "name": str(
                                    f.path
                                    if hasattr(f, 'path')
                                    else f.id
                                )
                            })
                    except Exception:
                        pass
                if result:
                    self._files = result
                    print(
                        f"   ✅ Found "
                        f"{len(result)} files"
                    )
                    return result

        except Exception as e:
            print(f"   ⚠️ Scan error: {e}")

        return []

    def get_total(self):
        return len(self._get_all_files())

    def download_by_id(self, file_id, name):
        """
        Download specific file by ID
        Used when resuming multi-part upload
        """
        return self._download(file_id, name)

    def download_random(self):
        """
        Pick random file and download
        Returns (local_path, file_id, name)
        """
        files = self._get_all_files()

        if not files:
            print("   ❌ No files found")
            return None, None, None

        audio   = random.choice(files)
        file_id = audio["id"]
        name    = audio["name"]

        print(f"   🎵 Selected: {name}")

        path = self._download(file_id, name)
        return path, file_id, name

    def _download(self, file_id, name):
        """Download file from Google Drive"""
        local_path = os.path.join(
            AUDIO_DIR,
            f"{file_id}.mp3"
        )

        # Use cache if valid
        if os.path.exists(local_path):
            size = os.path.getsize(local_path)
            if size > 1024 * 1024:
                print(
                    f"   ✅ Cached: "
                    f"{size // 1024 // 1024} MB"
                )
                return local_path
            else:
                os.remove(local_path)

        print(f"   📥 Downloading: {name}...")

        # Method 1: gdown
        result = self._gdown(file_id, local_path)
        if result:
            return result

        # Method 2: requests
        result = self._requests_dl(
            file_id, local_path
        )
        if result:
            return result

        print("   ❌ Download failed")
        return None

    def _gdown(self, file_id, local_path):
        """Download using gdown"""
        try:
            import gdown
            print("   🔄 Method 1: gdown...")

            url = (
                f"https://drive.google.com/uc"
                f"?id={file_id}"
            )
            result = gdown.download(
                url    = url,
                output = local_path,
                quiet  = False,
            )

            if result and os.path.exists(local_path):
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

    def _requests_dl(self, file_id, local_path):
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
                f"&id={file_id}&confirm=t"
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
