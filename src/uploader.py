"""
YouTube Uploader
Uploads videos with metadata and thumbnails
"""

import os
import time
import random
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
        thumbnail_path=None,
        privacy="public",
        tags=None
    ):
        """Upload video to YouTube"""

        if not os.path.exists(video_path):
            print(f"   ❌ Video file not found: {video_path}")
            return None

        size = os.path.getsize(video_path)
        print(
            f"   📤 Uploading: "
            f"{size // 1024 // 1024} MB"
        )

        if tags is None:
            tags = [
                "rain sounds",
                "deep sleep",
                "heavy rain",
                "sleep music",
                "relaxing rain",
                "rain asmr",
                "white noise",
                "sleep aid",
                "insomnia relief",
                "meditation",
                "stress relief",
                "study music",
            ]

        body = {
            "snippet": {
                "title"      : title[:100],
                "description": description[:5000],
                "tags"       : tags,
                "categoryId" : "22",  # People & Blogs
            },
            "status": {
                "privacyStatus"         : privacy,
                "selfDeclaredMadeForKids": False,
            },
        }

        try:
            media = MediaFileUpload(
                video_path,
                mimetype    = "video/mp4",
                resumable   = True,
                chunksize   = 1024 * 1024 * 10  # 10MB chunks
            )

            request  = self.youtube.videos().insert(
                part = "snippet,status",
                body = body,
                media_body = media
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(
                        status.progress() * 100
                    )
                    print(
                        f"   ⬆️ Upload: {progress}%",
                        end="\r"
                    )

            video_id  = response["id"]
            video_url = (
                f"https://www.youtube.com/watch?v={video_id}"
            )

            print(f"\n   ✅ Uploaded: {video_url}")

            # Set thumbnail
            if thumbnail_path and os.path.exists(
                thumbnail_path
            ):
                self._set_thumbnail(
                    video_id, thumbnail_path
                )

            return {
                "success"  : True,
                "video_id" : video_id,
                "url"      : video_url,
            }

        except HttpError as e:
            print(f"   ❌ HTTP Error: {e}")
            return None
        except Exception as e:
            print(f"   ❌ Upload error: {e}")
            return None

    def _set_thumbnail(self, video_id, thumbnail_path):
        """Set custom thumbnail"""
        try:
            self.youtube.thumbnails().set(
                videoId    = video_id,
                media_body = MediaFileUpload(
                    thumbnail_path,
                    mimetype="image/jpeg"
                )
            ).execute()
            print("   ✅ Thumbnail set")
        except Exception as e:
            print(f"   ⚠️ Thumbnail error: {e}")