"""
Audio Loader
Loads random audio from Google Drive Public Folder
Uses gdown to handle Google Drive downloads
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

            folder_url = (
                f"https://drive.google.com"
                f"/drive/folders/{self.folder_id}"
            )

            # Get folder contents
            # Returns list of GoogleDriveFileToDownload
            files = gdown.download_folder(
                url           = folder_url,
                skip_download = True,
                quiet         = False,
            )

            if files:
                result = []
                for f in files:
                    # Handle new gdown object type
                    if hasattr(f, 'id') and hasattr(f, 'name'):
                        result.append({
                            "id"  : f.id,
                            "name": f.name
                        })
                    elif hasattr(f, '__dict__'):
                        d = f.__dict__
                        result.append({
                            "id"  : d.get('id', ''),
                            "name": d.get('name', 'Rain Audio')
                        })
                    elif isinstance(f, dict):
                        result.append({
                            "id"  : f.get('id', ''),
                            "name": f.get('name', 'Rain Audio')
                        })
                    else:
                        # Try string representation
                        print(f"   📄 File object: {f}")

                # Filter valid entries
                result = [
                    r for r in result
                    if r.get('id')
                ]

                if result:
                    self._files = result
                    print(
                        f"   ✅ Found "
                        f"{len(result)} files"
                    )
                    return result

        except Exception as e:
            print(f"   ⚠️ gdown error: {e}")

        # Fallback: parse gdown output directly
        return self._get_files_from_logs()

    def _get_files_from_logs(self):
        """
        Fallback: use gdown to list files
        and parse the output
        """
        print("   🔄 Trying direct gdown listing...")
        try:
            import gdown
            import io
            import sys

            folder_url = (
                f"https://drive.google.com"
                f"/drive/folders/{self.folder_id}"
            )

            # Capture gdown output
            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()

            try:
                gdown.download_folder(
                    url           = folder_url,
                    skip_download = True,
                    quiet         = False,
                )
            except Exception:
                pass
            finally:
                sys.stdout = old_stdout

            output = buffer.getvalue()
            print(f"   📋 gdown output captured")

            # Parse file IDs from output
            # Format: "Processing file FILEID filename"
            pattern = r'Processing file ([\w-]+) (.+)'
            matches = re.findall(pattern, output)

            if matches:
                files = [
                    {
                        "id"  : m[0],
                        "name": m[1].strip()
                    }
                    for m in matches
                ]
                self._files = files
                print(
                    f"   ✅ Found "
                    f"{len(files)} files from logs"
                )
                return files

        except Exception as e:
            print(f"   ⚠️ Log parse error: {e}")

        # Last resort: hardcode from logs
        return self._get_files_hardcoded()

    def _get_files_hardcoded(self):
        """
        Last resort: use file IDs found
        from previous gdown output in logs
        """
        print("   🔄 Using detected file IDs...")

        # These IDs were found from your gdown logs
        files = [
            {
                "id"  : "1wfiuLyY4DAlPfr3gLX6oUm36f5ZHk1lS",
                "name": "Best Rain in the Forest at Night"
            }
        ]

        # Also scan folder page for more IDs
        try:
            headers  = {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64)"
                )
            }
            url      = (
                f"https://drive.google.com"
                f"/drive/folders/{self.folder_id}"
            )
            response = requests.get(
                url,
                headers = headers,
                timeout = 30
            )

            if response.status_code == 200:
                # Find all 33-char IDs
                all_ids = re.findall(
                    r'"([\w-]{33})"',
                    response.text
                )

                # Remove folder ID
                all_ids = list(set([
                    i for i in all_ids
                    if i != self.folder_id
                ]))

                # Add any new IDs not already in list
                existing = [f["id"] for f in files]
                for fid in all_ids:
                    if fid not in existing:
                        files.append({
                            "id"  : fid,
                            "name": f"Rain Audio {len(files)+1}"
                        })

        except Exception as e:
            print(f"   ⚠️ Scan error: {e}")

        self._files = files
        print(f"   ✅ Using {len(files)} files")
        return files

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
        Uses gdown for reliable downloading
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

        # Method 1: gdown
        result = self._gdown(file_id, local_path)
        if result:
            return result, name

        # Method 2: requests
        result = self._requests_dl(file_id, local_path)
        if result:
            return result, name

        print("   ❌ All methods failed")
        return None, None

    def _gdown(self, file_id, local_path):
        """Download using gdown"""
        try:
            import gdown
            print("   🔄 Method 1: gdown...")

            url = (
                f"https://drive.google.com/uc"
                f"?id={file_id}"
            )

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
