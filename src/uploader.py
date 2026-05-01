"""
YouTube Uploader
Upload first then add tags separately
Debug tag issues
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
        clean_title = re.sub(
            r'[^\x00-\x7F]+', '', str(title)
        ).strip()
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

        # Upload WITHOUT tags first
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

            # Add tags separately
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
        Add tags one by one to find bad tag
        Then add all good tags together
        """
        if not tags:
            return

        try:
            # Step 1: Clean all tags
            clean = []
            total = 0

            for tag in tags:
                # Only letters numbers spaces
                t = re.sub(
                    r'[^a-zA-Z0-9\s]',
                    '',
                    str(tag)
                ).strip().lower()

                # Remove extra spaces
                t = ' '.join(t.split())

                if not t or len(t) < 2:
                    continue

                if len(t) > 30:
                    t = t[:30].strip()

                if t in clean:
                    continue

                if total + len(t) + 1 > 490:
                    break

                clean.append(t)
                total += len(t) + 1

            if not clean:
                print("   ⚠️ No valid tags")
                return

            print(
                f"   🏷️ Testing {len(clean)} tags..."
            )

            # Step 2: Find bad tags
            # Test with small batches of 5
            good_tags = []

            for i in range(0, len(clean), 5):
                batch = clean[i:i+5]

                try:
                    # Get current snippet
                    resp = self.youtube.videos().list(
                        part="snippet",
                        id=video_id
                    ).execute()

                    if not resp.get("items"):
                        return

                    snippet = (
                        resp["items"][0]["snippet"]
                    )
                    snippet["tags"] = (
                        good_tags + batch
                    )

                    self.youtube.videos().update(
                        part="snippet",
                        body={
                            "id"     : video_id,
                            "snippet": snippet
                        }
                    ).execute()

                    # Batch is good
                    good_tags.extend(batch)
                    print(
                        f"   ✅ Batch {i//5+1} ok: "
                        f"{batch}"
                    )

                except Exception as e:
                    print(
                        f"   ⚠️ Batch {i//5+1} "
                        f"failed: {batch}"
                    )
                    print(f"   🔍 Error: {e}")

                    # Try tags one by one
                    for single_tag in batch:
                        try:
                            resp = (
                                self.youtube
                                .videos()
                                .list(
                                    part="snippet",
                                    id=video_id
                                ).execute()
                            )

                            if not resp.get("items"):
                                continue

                            snippet = (
                                resp["items"][0]
                                ["snippet"]
                            )
                            snippet["tags"] = (
                                good_tags
                                + [single_tag]
                            )

                            self.youtube.videos(
                            ).update(
                                part="snippet",
                                body={
                                    "id": video_id,
                                    "snippet": snippet
                                }
                            ).execute()

                            good_tags.append(
                                single_tag
                            )
                            print(
                                f"   ✅ Tag ok: "
                                f"{single_tag}"
                            )

                        except Exception:
                            print(
                                f"   ❌ Bad tag: "
                                f"{single_tag}"
                            )

            print(
                f"   ✅ Tags done: "
                f"{len(good_tags)} added"
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
