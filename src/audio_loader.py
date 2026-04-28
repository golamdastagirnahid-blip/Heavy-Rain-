"""
Audio Loader
Loads random audio from Google Drive Public Folder
Uses gdown to handle Google Drive downloads
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
        self.folder_id = data.get("folder_id", "")
        self._files    = []

    def _get_all_files(self):
        """
        Get all files from Google Drive folder
        by parsing gdown output
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

            # Capture gdown printed output
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = buf_out = io.StringIO()
            sys.stderr = buf_err = io.StringIO()

            try:
                files = gdown.download_folder(
                    url           = folder_url,
                    skip_download = True,
                    quiet         = False,
                )
            except Exception:
                files = None
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr

            output = buf_out.getvalue()
            output += buf_err.getvalue()

            # Parse file IDs from output
            # Format: Processing file FILEID filename
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

            # Also try parsing file objects directly
            if files:
                result = []
                for f in files:
                    try:
                        if hasattr(f, 'id'):
                            result.append({
                                "id"  : str(f.id),
                                "name": str(f.path) if hasattr(f, 'path') else str(f.id)
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
            print(f"   ⚠️ Folder scan error: {e}")

        print("   ❌ Could not list folder files")
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
        Download file from Google Drive
        """
        # Clean filename for local storage
        safe_name  = re.sub(r'[^\w\-_.]', '_', name)
        local_path = os.path.join(
            AUDIO_DIR,
            f"{file_id}.mp3"
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

        # Method 1: gdown (no fuzzy)
        result = self._gdown(file_id, local_path)
        if result:
            return result, name

        # Method 2: gdown with folder path
        result = self._gdown_folder(
            file_id, name, local_path
        )
        if result:
            return result, name

        # Method 3: requests with session
        result = self._requests_dl(file_id, local_path)
        if result:
            return result, name

        print("   ❌ All methods failed")
        return None, None

    def _gdown(self, file_id, local_path):
        """Download using gdown without fuzzy"""
        try:
            import gdown
            print("   🔄 Method 1: gdown direct...")

            url = (
                f"https://drive.google.com/uc"
                f"?id={file_id}"
            )

            # Use output parameter
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
            print(f"   ⚠️ Method 1 error: {e}")
            return None

    def _gdown_folder(self, file_id, name, local_path):
        """
        Download by getting file from
        already downloaded folder contents
        """
        try:
            import gdown
            print("   🔄 Method 2: gdown folder...")

            folder_url = (
                f"https://drive.google.com"
                f"/drive/folders/{self.folder_id}"
            )

            # Download entire folder to temp dir
            temp_dir = os.path.join(
                os.path.dirname(local_path),
                "temp_folder"
            )
            os.makedirs(temp_dir, exist_ok=True)

            gdown.download_folder(
                url    = folder_url,
                output = temp_dir,
                quiet  = False,
            )

            # Find downloaded audio file
            for root, dirs, files in os.walk(temp_dir):
                for fname in files:
                    if fname.endswith((
                        '.mp3', '.m4a',
                        '.wav', '.ogg', '.flac'
                    )):
                        src = os.path.join(root, fname)
                        import shutil
                        shutil.move(src, local_path)

                        size = os.path.getsize(local_path)
                        if size > 1024 * 100:
                            print(
                                f"   ✅ Downloaded: "
                                f"{size // 1024 // 1024} MB"
                            )
                            # Cleanup temp
                            shutil.rmtree(
                                temp_dir,
                                ignore_errors=True
                            )
                            return local_path

        except Exception as e:
            print(f"   ⚠️ Method 2 error: {e}")

        return None

    def _requests_dl(self, file_id, local_path):
        """Download using requests with proper headers"""
        try:
            print("   🔄 Method 3: requests...")
            session = requests.Session()

            # First visit the file page
            file_page = (
                f"https://drive.google.com"
                f"/file/d/{file_id}/view"
            )
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,"
                    "application/xml;q=0.9,*/*;q=0.8"
                ),
            }
            session.get(
                file_page,
                headers = headers,
                timeout = 30
            )

            # Now download
            download_url = (
                f"https://drive.google.com/uc"
                f"?export=download"
                f"&id={file_id}"
                f"&confirm=t"
                f"&uuid=b49d3a49-4421-4b76-b9b4-797c81284b9f"
            )

            response = session.get(
                download_url,
                headers = headers,
                stream  = True,
                timeout = 300,
                allow_redirects = True
            )

            content_type = response.headers.get(
                "Content-Type", ""
            )

            print(
                f"   📋 Content-Type: {content_type}"
            )
            print(
                f"   📋 Status: {response.status_code}"
            )

            if "text/html" in content_type:
                # Try to find real download URL in HTML
                token = re.search(
                    r'confirm=([^&"\'>\s]+)',
                    response.text
                )
                if token:
                    real_url = (
                        f"https://drive.google.com/uc"
                        f"?export=download"
                        f"&id={file_id}"
                        f"&confirm={token.group(1)}"
                    )
                    response = session.get(
                        real_url,
                        headers = headers,
                        stream  = True,
                        timeout = 300
                    )
                    content_type = response.headers.get(
                        "Content-Type", ""
                    )
                    if "text/html" in content_type:
                        print("   ⚠️ Still HTML")
                        return None
                else:
                    print("   ⚠️ No token found")
                    return None

            if response.status_code == 200:
                with open(local_path, "wb") as f:
                    downloaded = 0
                    for chunk in response.iter_content(
                        chunk_size=32768
                    ):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)

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
            print(f"   ⚠️ Method 3 error: {e}")
            return None
