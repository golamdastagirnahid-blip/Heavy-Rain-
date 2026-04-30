"""
YouTube Uploader
Uploads videos with SEO optimized metadata
"""

import os
import time
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
        """
        Upload video to YouTube
        With SEO optimized metadata
        """
        if not os.path.exists(video_path):
            print(
                f"   ❌ Video not found: "
                f"{video_path}"
            )
            return None

        size = os.path.getsize(video_path)
        print(
            f"   📤 Uploading: "
            f"{size // 1024 // 1024} MB"
        )

        # Default SEO tags if none provided
        if not tags:
            tags = [
                "rain sounds",
                "deep sleep",
                "heavy rain",
                "sleep music",
                "white noise",
                "rain sounds for sleeping",
                "heavy rain sounds",
                "sleep aid",
                "insomnia relief",
                "relaxing rain",
                "rain asmr",
                "nature sounds",
                "ambient sounds",
                "study music",
                "meditation music",
            ]

        body = {
            "snippet": {
                "title"      : title[:100],
                "description": description[:5000],
                "tags"       : tags,
                "categoryId" : "22",
                "defaultLanguage"      : "en",
                "defaultAudioLanguage" : "en",
            },
            "status": {
                "privacyStatus"         : privacy,
                "selfDeclaredMadeForKids": False,
                "madeForKids"            : False,
            },
        }

        try:
            media = MediaFileUpload(
                video_path,
                mimetype   = "video/mp4",
                resumable  = True,
                chunksize  = 1024 * 1024 * 10
            )

            request  = self.youtube.videos().insert(
                part       = "snippet,status",
                body       = body,
                media_body = media
            )

            response = None
            while response is None:
                status, response = (
                    request.next_chunk()
                )
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
                f"https://www.youtube.com"
                f"/watch?v={video_id}"
            )

            print(
                f"\n   ✅ Uploaded: {video_url}"
            )

            # Set thumbnail if provided
            if (
                thumbnail_path
                and os.path.exists(thumbnail_path)
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

    def _set_thumbnail(
        self, video_id, thumbnail_path
    ):
        """Set custom thumbnail"""
        try:
            self.youtube.thumbnails().set(
                videoId    = video_id,
                media_body = MediaFileUpload(
                    thumbnail_path,
                    mimetype="image/jpeg"
                )
            ).execute()
            print("   ✅ Thumbnail uploaded")
        except Exception as e:
            print(
                f"   ⚠️ Thumbnail error: {e}"
            )
