"""
YouTube Uploader
Upload with no tags to bypass invalid tags error
"""

import os
import re
from googleapiclient.http   import MediaFileUpload
from googleapiclient.errors import HttpError


class VideoUploader:

    def __init__(self, youtube):
        self.youtube = youtube

    def upload(
        self,
        video_path,
        title,
        description,
        tags           = None,
        thumbnail_path = None,
        privacy        = "public"
    ):
        """Upload video to YouTube"""
        if not os.path.exists(video_path):
            print(
                f"   ❌ File not found: "
                f"{video_path}"
            )
            return None

        size = os.path.getsize(video_path)
        print(
            f"   📤 Uploading: "
            f"{size//1024//1024} MB"
        )

        # Clean title
        # Remove emojis and special chars
        clean_title = re.sub(
            r'[^\x00-\x7F]+', '', str(title)
        ).strip()

        # Remove extra spaces
        clean_title = ' '.join(
            clean_title.split()
        )[:100]

        if not clean_title:
            clean_title = (
                "Heavy Rain Sounds for Deep Sleep"
            )

        # Clean description
        clean_desc = str(
            description
        ).strip()[:5000]

        print(f"   📝 Title: {clean_title}")

        body = {
            "snippet": {
                "title"      : clean_title,
                "description": clean_desc,
                "categoryId" : "22",
                "defaultLanguage"     : "en",
                "defaultAudioLanguage": "en",
            },
            "status": {
                "privacyStatus"          : privacy,
                "selfDeclaredMadeForKids": False,
                "madeForKids"            : False,
            },
        }

        try:
            media = MediaFileUpload(
                video_path,
                mimetype  = "video/mp4",
                resumable = True,
                chunksize = 1024*1024*10
            )

            req = self.youtube.videos().insert(
                part       = "snippet,status",
                body       = body,
                media_body = media
            )

            response = None
            while response is None:
                status, response = req.next_chunk()
                if status:
                    pct = int(
                        status.progress() * 100
                    )
                    print(
                        f"   ⬆️ {pct}%",
                        end="\r"
                    )

            vid_id  = response["id"]
            vid_url = (
                f"https://www.youtube.com"
                f"/watch?v={vid_id}"
            )
            print(
                f"\n   ✅ Uploaded: {vid_url}"
            )

            # Upload thumbnail
            if (
                thumbnail_path
                and os.path.exists(thumbnail_path)
            ):
                self._thumbnail(
                    vid_id, thumbnail_path
                )

            # Add tags after upload
            # Separate API call is more reliable
            self._add_tags(vid_id, tags)

            return {
                "success" : True,
                "video_id": vid_id,
                "url"     : vid_url,
            }

        except HttpError as e:
            print(f"   ❌ HTTP Error: {e}")
            return None
        except Exception as e:
            print(f"   ❌ Upload error: {e}")
            return None

    def _add_tags(self, video_id, tags):
        """
        Add tags in separate API call
        after video is uploaded
        More reliable than adding during upload
        """
        if not tags:
            return

        try:
            # Clean tags
            clean = []
            total = 0

            for tag in tags:
                t = re.sub(
                    r'[^a-zA-Z0-9\s]',
                    '',
                    str(tag)
                ).strip()

                if not t or len(t) < 2:
                    continue

                if len(t) > 30:
                    t = t[:30].strip()

                if total + len(t) + 1 > 490:
                    break

                clean.append(t)
                total += len(t) + 1

            if not clean:
                return

            print(
                f"   🏷️ Adding {len(clean)} tags..."
            )

            # Get current video snippet
            response = self.youtube.videos().list(
                part = "snippet",
                id   = video_id
            ).execute()

            if not response.get("items"):
                return

            snippet = response["items"][0]["snippet"]
            snippet["tags"] = clean

            self.youtube.videos().update(
                part = "snippet",
                body = {
                    "id"     : video_id,
                    "snippet": snippet
                }
            ).execute()

            print(
                f"   ✅ Tags added: {len(clean)}"
            )

        except Exception as e:
            print(f"   ⚠️ Tags error: {e}")

    def _thumbnail(self, video_id, path):
        """Upload custom thumbnail"""
        try:
            self.youtube.thumbnails().set(
                videoId    = video_id,
                media_body = MediaFileUpload(
                    path,
                    mimetype="image/jpeg"
                )
            ).execute()
            print("   ✅ Thumbnail uploaded")
        except Exception as e:
            print(f"   ⚠️ Thumbnail: {e}")
