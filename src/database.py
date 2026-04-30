"""
Database Manager
Tracks uploaded videos and statistics
"""

import os
import json
from datetime import datetime


class Database:

    def __init__(self):
        self.db_file = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)
                )
            ),
            "database.json"
        )
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r") as f:
                    data = json.load(f)
                if "uploaded_videos" not in data:
                    data["uploaded_videos"] = []
                if "daily_counts" not in data:
                    data["daily_counts"] = {}
                if "statistics" not in data:
                    data["statistics"] = {
                        "total_uploads": 0
                    }
                return data
            except Exception:
                pass
        return {
            "uploaded_videos": [],
            "daily_counts"   : {},
            "statistics"     : {
                "total_uploads": 0
            },
        }

    def save(self):
        with open(self.db_file, "w") as f:
            json.dump(self.data, f, indent=4)

    def is_uploaded(self, video_id):
        return video_id in self.data.get(
            "uploaded_videos", []
        )

    def mark_uploaded(self, video_id, info={}):
        if video_id not in (
            self.data["uploaded_videos"]
        ):
            self.data[
                "uploaded_videos"
            ].append(video_id)
            self.data[
                "statistics"
            ]["total_uploads"] += 1
            today = datetime.now().strftime(
                "%Y-%m-%d"
            )
            self.data["daily_counts"][today] = (
                self.data["daily_counts"].get(
                    today, 0
                ) + 1
            )
            self.save()

    def get_today_count(self):
        today = datetime.now().strftime(
            "%Y-%m-%d"
        )
        return self.data[
            "daily_counts"
        ].get(today, 0)

    def get_statistics(self):
        return self.data.get(
            "statistics",
            {"total_uploads": 0}
        )
