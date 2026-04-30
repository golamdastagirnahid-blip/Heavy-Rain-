"""
Audio Loader
Loads random audio from Google Drive
Public Folder using gdown
With caching to avoid rate limits
"""

import os
import re
import io
import sys
import json
import time
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

            old_out    = sys.stdout
            old_err    = sys.stderr
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
            pattern = (
                r'Processing file ([\w-]+) (.+)'
            )
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

            # Try file objects directly
            if files:
                result = []
                for f in files:
                    try:
                        if hasattr(f, 'id'):
                            result.append({
                                "id": str(f.id),
                                "name": str(
                                    f.path
                                    if hasattr(
                                        f, 'path'
                                    )
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
        """Return total number of audio files"""
        return len(self._get_all_files())

    def download_by_id(self, file_id, name):
        """
        Download specific file by ID
        Used when resuming multi-part upload
        Always checks cache first
        Never re-downloads if cached
        """
        print(
            f"   🔍 Checking cache for: {name}"
        )

        # Check all possible extensions
        for ext in ['mp3', 'm4a', 'wav', 'ogg']:
            local_path = os.path.join(
                AUDIO_DIR, f"{file_id}.{ext}"
            )
            if os.path.exists(local_path):
                size = os.path.getsize(local_path)
                if size > 1024 * 1024:
                    print(
                        f"   ✅ Found in cache: "
                        f"{size//1024//1024} MB"
                    )
                    return local_path
                else:
                    # Remove corrupt cache
                    os.remove(local_path)

        # Search by file_id in audio dir
        if os.path.exists(AUDIO_DIR):
            for fname in os.listdir(AUDIO_DIR):
                if file_id in fname:
                    fpath = os.path.join(
                        AUDIO_DIR, fname
                    )
                    if os.path.exists(fpath):
                        size = os.path.getsize(
                            fpath
                        )
                        if size > 1024 * 1024:
                            print(
                                f"   ✅ Found: "
                                f"{fname} "
                                f"({size//1024//1024} MB)"
                            )
                            return fpath

        # Not in cache - must download
        print(
            f"   📥 Not cached - downloading..."
        )
        return self._download(file_id, name)

    def download_random(self):
        """
        Pick random audio file and download it
        Returns (local_path, file_id, name)
        """
        files = self._get_all_files()

        if not files:
            print("   ❌ No files found in folder")
            return None, None, None

        # Pick random file
        audio   = random.choice(files)
        file_id = audio["id"]
        name    = audio["name"]

        print(f"   🎵 Selected: {name}")

        path = self._download(file_id, name)
        return path, file_id, name

    def _download(self, file_id, name):
        """
        Download with multiple methods
        and retry logic
        Checks cache first
        """
        # Check cache for all extensions
        for ext in ['mp3', 'm4a', 'wav', 'ogg']:
            local_path = os.path.join(
                AUDIO_DIR, f"{file_id}.{ext}"
            )
            if os.path.exists(local_path):
                size = os.path.getsize(local_path)
                if size > 1024 * 1024:
                    print(
                        f"   ✅ Cached: "
                        f"{size//1024//1024} MB"
                    )
                    return local_path
                else:
                    os.remove(local_path)

        # Default save path
        local_path = os.path.join(
            AUDIO_DIR, f"{file_id}.mp3"
        )

        print(f"   📥 Downloading: {name}...")

        # Method 1: gdown with retry
        result = self._gdown_retry(
            file_id, local_path
        )
        if result:
            return result

        # Method 2: requests direct
        result = self._requests_direct(
            file_id, local_path
        )
        if result:
            return result

        # Method 3: requests with session
        result = self._requests_session(
            file_id, local_path
        )
        if result:
            return result

        print("   ❌ All methods failed")
        return None

    def _gdown_retry(
        self, file_id, local_path, retries=3
    ):
        """gdown with retry and wait"""
        try:
            import gdown
        except ImportError:
            print("   ⚠️ gdown not installed")
            return None

        for attempt in range(1, retries + 1):
            try:
                print(
                    f"   🔄 gdown attempt "
                    f"{attempt}/{retries}..."
                )

                # Clean failed download
                if os.path.exists(local_path):
                    os.remove(local_path)

                url = (
                    f"https://drive.google.com/uc"
                    f"?id={file_id}"
                )

                result = gdown.download(
                    url    = url,
                    output = local_path,
                    quiet  = False,
                )

                if (
                    result
                    and os.path.exists(local_path)
                ):
                    size = os.path.getsize(
                        local_path
                    )
                    if size > 1024 * 100:
                        print(
                            f"   ✅ Downloaded: "
                            f"{size//1024//1024} MB"
                        )
                        return local_path

                # Wait before retry
                if attempt < retries:
                    wait = attempt * 30
                    print(
                        f"   ⏳ Waiting {wait}s "
                        f"before retry..."
                    )
                    time.sleep(wait)

            except Exception as e:
                err = str(e)[:120]
                print(
                    f"   ⚠️ gdown attempt "
                    f"{attempt} failed: {err}"
                )
                if attempt < retries:
                    wait = attempt * 30
                    print(
                        f"   ⏳ Waiting {wait}s..."
                    )
                    time.sleep(wait)

        return None

    def _requests_direct(
        self, file_id, local_path
    ):
        """Direct download using requests"""
        try:
            print(
                "   🔄 Method 2: "
                "requests direct..."
            )
            session = requests.Session()
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
            url = (
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

            ct = response.headers.get(
                "Content-Type", ""
            )
            if "text/html" in ct:
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
                        f"{size//1024//1024} MB"
                    )
                    return local_path

            if os.path.exists(local_path):
                os.remove(local_path)
            return None

        except Exception as e:
            print(f"   ⚠️ Method 2 error: {e}")
            if os.path.exists(local_path):
                os.remove(local_path)
            return None

    def _requests_session(
        self, file_id, local_path
    ):
        """Session based download with cookies"""
        try:
            print(
                "   🔄 Method 3: "
                "session download..."
            )
            session = requests.Session()
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Macintosh; Intel Mac OS X "
                    "10_15_7) AppleWebKit/537.36"
                )
            }

            # Visit file page to get cookies
            session.get(
                f"https://drive.google.com"
                f"/file/d/{file_id}/view",
                headers = headers,
                timeout = 30
            )

            # Download with cookies
            url = (
                f"https://drive.google.com/uc"
                f"?export=download"
                f"&id={file_id}&confirm=t"
            )
            response = session.get(
                url,
                headers         = headers,
                stream          = True,
                timeout         = 300,
                allow_redirects = True
            )

            ct = response.headers.get(
                "Content-Type", ""
            )

            # Handle HTML response
            if "text/html" in ct:
                token = re.search(
                    r'confirm=([^&"\'>\s]+)',
                    response.text
                )
                if token:
                    real_url = (
                        f"https://drive.google.com"
                        f"/uc?export=download"
                        f"&id={file_id}"
                        f"&confirm={token.group(1)}"
                    )
                    response = session.get(
                        real_url,
                        headers = headers,
                        stream  = True,
                        timeout = 300
                    )
                    ct = response.headers.get(
                        "Content-Type", ""
                    )
                    if "text/html" in ct:
                        print(
                            "   ⚠️ Still HTML"
                        )
                        return None
                else:
                    print(
                        "   ⚠️ No token found"
                    )
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
                        f"{size//1024//1024} MB"
                    )
                    return local_path

            if os.path.exists(local_path):
                os.remove(local_path)
            return None

        except Exception as e:
            print(f"   ⚠️ Method 3 error: {e}")
            if os.path.exists(local_path):
                os.remove(local_path)
            return None
