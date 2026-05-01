"""
YouTube Uploader
SEO optimized metadata upload
With strict tag validation
"""

import os
import re
from googleapiclient.http   import MediaFileUpload
from googleapiclient.errors import HttpError


class VideoUploader:

    def __init__(self, youtube):
        self.youtube = youtube

    def _clean_tags(self, tags):
        """
        Strictly clean tags for YouTube API
        Very strict validation
        """
        if not tags:
            return []

        clean = []
        total = 0

        for tag in tags:
            # Convert to string
            t = str(tag).strip()

            # Keep only letters numbers
            # spaces and hyphens
            t = re.sub(
                r'[^a-zA-Z0-9\s\-]', '', t
            )
            t = t.strip()

            # Skip empty
            if not t:
                continue

            # Skip too short
            if len(t) < 2:
                continue

            # Max 30 chars
            if len(t) > 30:
                t = t[:30].strip()

            # Skip if empty after trim
            if not t:
                continue

            # Check total length
            if total + len(t) + 1 > 450:
                break

            clean.append(t)
            total += len(t) + 1

        print(
            f"   🏷️ Valid tags: {len(clean)}"
        )
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

        # Safe default tags
        if not tags:
            tags = [
                "rain sounds",
                "deep sleep",
                "heavy rain",
                "sleep music",
                "white noise",
            ]

        # Strictly clean tags
        clean_tags = self._clean_tags(tags)

        # Clean title - remove emojis
        clean_title = re.sub(
            r'[^\x00-\x7F]+', '', str(title)
        ).strip()[:100]

        # If title empty after cleaning use default
        if not clean_title:
            clean_title = (
                "Heavy Rain Sounds for Deep Sleep"
            )

        # Clean description
        clean_desc = str(
            description
        ).strip()[:5000]

        print(f"   📝 Title: {clean_title}")
        print(
            f"   🏷️ Tags : {len(clean_tags)}"
        )

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

            return {
                "success" : True,
                "video_id": vid_id,
                "url"     : vid_url,
            }

        except HttpError as e:
            print(f"   ❌ HTTP Error: {e}")
            # Print exact tags for debugging
            print(
                f"   🔍 Tags sent: {clean_tags}"
            )
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
