"""
YouTube Authentication
Handles OAuth2 for YouTube API
"""

import os
import json
import google.auth.transport.requests
from google.oauth2.credentials        import Credentials
from google_auth_oauthlib.flow        import InstalledAppFlow
from googleapiclient.discovery        import build


SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]


class YouTubeAuth:

    def authenticate(self):
        """Authenticate and return YouTube service"""
        print("🔐 Authenticating YouTube...")

        creds = None

        # Load token if exists
        if os.path.exists("token.json"):
            try:
                creds = Credentials.from_authorized_user_file(
                    "token.json", SCOPES
                )
                print("   ✅ Token loaded")
            except Exception as e:
                print(f"   ⚠️ Token error: {e}")
                creds = None

        # Refresh if expired
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(
                    google.auth.transport.requests.Request()
                )
                print("   ✅ Token refreshed")
                self._save_token(creds)
            except Exception as e:
                print(f"   ⚠️ Refresh error: {e}")
                creds = None

        if not creds:
            print("   ❌ No valid credentials!")
            return None

        try:
            youtube = build(
                "youtube", "v3", credentials=creds
            )
            print("   ✅ YouTube API ready")
            return youtube
        except Exception as e:
            print(f"   ❌ Build error: {e}")
            return None

    def _save_token(self, creds):
        with open("token.json", "w") as f:
            f.write(creds.to_json())