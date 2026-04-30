"""
YouTube Uploader
SEO optimized metadata upload
"""

import os
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
        """Upload video with SEO metadata"""
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

        if not tags:
            tags = [
                "rain sounds",
                "deep sleep",
                "heavy rain",
                "sleep music",
                "white noise",
            ]

        body = {
            "snippet": {
                "title"      : title[:100],
                "description": description[:5000],
                "tags"       : tags[:30],
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

            req  = self.youtube.videos().insert(
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
            print(f"\n   ✅ Uploaded: {vid_url}")

            # Upload thumbnail
            if (
                thumbnail_path
                and os.path.exists(thumbnail_path)
            ):
                self._thumbnail(
                    vid_id, thumbnail_path
                )

            return {
                "success" : True,
                "video_id": vid_id,
                "url"     : vid_url,
            }

        except HttpError as e:
            print(f"   ❌ HTTP: {e}")
            return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None

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
