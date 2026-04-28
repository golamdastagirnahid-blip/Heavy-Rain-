"""
Database Manager
Tracks uploaded videos and audio rotation
"""

import os
import json
from datetime import datetime


class Database:

    def __init__(self):
        self.db_file = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            ),
            "database.json"
        )
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "uploaded_videos" : [],
            "daily_counts"    : {},
            "statistics"      : {"total_uploads": 0},
            "last_audio_index": 0,
            "last_footage_url": "",
        }

    def save(self):
        with open(self.db_file, "w") as f:
            json.dump(self.data, f, indent=4)

    def is_uploaded(self, video_id):
        return video_id in self.data.get(
            "uploaded_videos", []
        )

    def mark_uploaded(self, video_id, info={}):
        if video_id not in self.data["uploaded_videos"]:
            self.data["uploaded_videos"].append(video_id)
            self.data["statistics"]["total_uploads"] += 1
            today = datetime.now().strftime("%Y-%m-%d")
            self.data["daily_counts"][today] = (
                self.data["daily_counts"].get(today, 0) + 1
            )
            self.save()

    def get_next_audio_index(self, total):
        current = self.data.get("last_audio_index", 0)
        next_index = (current + 1) % total
        self.data["last_audio_index"] = next_index
        self.save()
        return current

    def get_today_count(self):
        today = datetime.now().strftime("%Y-%m-%d")
        return self.data["daily_counts"].get(today, 0)

    def get_statistics(self):
        return self.data.get(
            "statistics", {"total_uploads": 0}
        )

    def set_last_footage(self, url):
        self.data["last_footage_url"] = url
        self.save()

    def get_last_footage(self):
        return self.data.get("last_footage_url", "")