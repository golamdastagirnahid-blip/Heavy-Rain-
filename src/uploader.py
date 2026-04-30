"""
YouTube Uploader
SEO optimized metadata upload
With tag validation
"""

import os
from googleapiclient.http   import MediaFileUpload
from googleapiclient.errors import HttpError


class VideoUploader:

    def __init__(self, youtube):
        self.youtube = youtube

    def _clean_tags(self, tags):
        """
        Clean and validate tags for YouTube
        Remove invalid characters
        Enforce length limits
        """
        if not tags:
            return []

        clean = []
        total = 0

        for tag in tags:
            # Convert to string and strip
            t = str(tag).strip()

            # Remove invalid chars
            t = t.replace('"', '')
            t = t.replace("'", '')
            t = t.replace('<', '')
            t = t.replace('>', '')
            t = t.replace('&', 'and')
            t = t.replace('\n', ' ')
            t = t.replace('\r', ' ')
            t = t.strip()

            # Skip empty tags
            if not t:
                continue

            # Max 30 chars per tag
            if len(t) > 30:
                t = t[:30].strip()

            # Skip if still empty
            if not t:
                continue

            # YouTube 500 char total limit
            if total + len(t) + 1 > 490:
                break

            clean.append(t)
            total += len(t) + 1

        return clean

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

        # Default safe tags
        if not tags:
            tags = [
                "rain sounds",
                "deep sleep",
                "heavy rain",
                "sleep music",
                "white noise",
            ]

        # Clean and validate tags
        clean_tags = self._clean_tags(tags)
        print(
            f"   🏷️ Tags: {len(clean_tags)}"
        )

        # Clean title
        clean_title = str(title).strip()[:100]

        # Clean description
        clean_desc  = str(
            description
        ).strip()[:5000]

        body = {
            "snippet": {
                "title"      : clean_title,
                "description": clean_desc,
                "tags"       : clean_tags,
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
