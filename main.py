"""
Heavy Rain Deep Sleep - YouTube Automation
Main entry point
Picks random audio from Google Drive folder
Gets stock footage from Pexels/Pixabay
Loops footage over audio
Uploads to YouTube
"""

import os
import sys
import time
import random
from datetime import datetime

from src.database            import Database
from src.audio_loader        import AudioLoader
from src.footage_downloader  import FootageDownloader
from src.video_processor     import VideoProcessor
from src.ai_generator        import AIGenerator
from src.thumbnail_generator import ThumbnailGenerator
from src.auth                import YouTubeAuth
from src.uploader            import VideoUploader


# Max 4 hours per part
MAX_PART_SECONDS = 4 * 60 * 60


def format_duration(seconds):
    hours   = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}h {minutes}m"


def main():
    print("=" * 60)
    print("🌧️  Heavy Rain Deep Sleep Automation")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Initialize all components
    db        = Database()
    loader    = AudioLoader()
    footage   = FootageDownloader()
    processor = VideoProcessor()
    ai        = AIGenerator()
    thumb_gen = ThumbnailGenerator()
    auth      = YouTubeAuth()

    # Check daily limit
    today_count = db.get_today_count()
    print(f"\n📊 Today's uploads: {today_count}/3")

    if today_count >= 3:
        print("✅ Daily limit reached (3 videos)")
        print("   Will resume tomorrow")
        return

    # Authenticate YouTube
    youtube = auth.authenticate()
    if not youtube:
        print("❌ YouTube authentication failed!")
        sys.exit(1)

    uploader = VideoUploader(youtube)

    # Get random audio from Google Drive folder
    print("\n📥 Loading random audio...")
    audio_path, audio_name = loader.download_random()
    if not audio_path:
        print("❌ Audio download failed!")
        sys.exit(1)

    print(f"   ✅ Using: {audio_name}")

    # Get audio duration
    print("\n⏱️ Checking audio duration...")
    audio_duration = processor.get_duration(audio_path)
    if audio_duration == 0:
        print("❌ Could not get audio duration!")
        sys.exit(1)

    print(
        f"   Duration: "
        f"{format_duration(audio_duration)}"
    )

    # Calculate parts
    num_parts = processor.calculate_parts(audio_duration)
    print(f"   Parts: {num_parts}")

    # Get stock footage
    print("\n🎬 Getting stock footage...")
    footage_path = footage.get_footage()
    if not footage_path:
        print("❌ Footage download failed!")
        sys.exit(1)

    # Generate unique video ID
    video_id = (
        f"rain_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

    # Generate AI metadata
    print("\n🤖 Generating metadata...")
    ai_title, ai_desc = ai.generate_metadata(
        audio_name, None, num_parts
    )
    print(f"   Title: {ai_title}")

    # Process and upload each part
    success_count = 0

    for part_num in range(1, num_parts + 1):

        print(f"\n{'='*60}")
        print(f"🎬 Part {part_num}/{num_parts}")
        print(f"{'='*60}")

        start_sec     = (part_num - 1) * MAX_PART_SECONDS
        end_sec       = min(
            part_num * MAX_PART_SECONDS,
            audio_duration
        )
        part_duration = end_sec - start_sec

        print(
            f"   ⏱️ "
            f"{format_duration(start_sec)} → "
            f"{format_duration(end_sec)}"
        )

        # Generate thumbnail
        print("\n🖼️ Generating thumbnail...")
        thumb_path = thumb_gen.generate(
            title        = ai_title,
            part_num     = part_num if num_parts > 1
                           else None,
            total_parts  = num_parts if num_parts > 1
                           else None,
            duration_str = format_duration(part_duration)
        )

        # Create video
        print("\n🎥 Creating video...")
        part_output_id = f"{video_id}_part{part_num}"
        video_path = processor.create_video(
            audio_path     = audio_path,
            footage_path   = footage_path,
            output_id      = part_output_id,
            start_sec      = start_sec,
            end_sec        = end_sec,
            thumbnail_path = thumb_path
        )

        if not video_path:
            print(
                f"❌ Video creation failed "
                f"for part {part_num}"
            )
            continue

        # Build title and description
        if num_parts > 1:
            part_title = (
                f"{ai_title} "
                f"| Part {part_num}/{num_parts}"
            )
        else:
            part_title = ai_title

        part_desc = (
            f"{ai_desc}\n\n"
            f"⏱️ Duration: "
            f"{format_duration(part_duration)}\n"
        )
        if num_parts > 1:
            part_desc += (
                f"📌 Part {part_num} "
                f"of {num_parts}\n"
            )

        # Upload to YouTube
        print(f"\n📤 Uploading Part {part_num}...")
        result = uploader.upload(
            video_path     = video_path,
            title          = part_title,
            description    = part_desc,
            thumbnail_path = thumb_path,
            privacy        = "public",
        )

        if result and result.get("success"):
            print(
                f"   ✅ Part {part_num} uploaded: "
                f"{result['url']}"
            )
            success_count += 1

            # Mark in database
            db.mark_uploaded(
                f"{part_output_id}",
                {
                    "title": part_title,
                    "url"  : result["url"],
                    "audio": audio_name,
                }
            )
        else:
            print(f"   ❌ Part {part_num} failed")

        # Cleanup video file to save space
        if video_path and os.path.exists(video_path):
            try:
                os.remove(video_path)
                print("   🗑️ Temp video deleted")
            except Exception:
                pass

        # Wait between parts (humanized)
        if part_num < num_parts:
            wait = random.randint(30, 90)
            print(f"\n⏳ Waiting {wait}s...")
            time.sleep(wait)

    # Final cleanup
    print("\n🧹 Cleaning up...")
    for path in [audio_path]:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass

    # Cleanup footage
    if footage_path and os.path.exists(footage_path):
        try:
            os.remove(footage_path)
        except Exception:
            pass

    # Cleanup thumbnails
    import glob
    for f in glob.glob("thumbnails/*.jpg"):
        try:
            os.remove(f)
        except Exception:
            pass

    # Summary
    print("\n" + "=" * 60)
    print(
        f"✅ Done! "
        f"{success_count}/{num_parts} parts uploaded"
    )
    stats = db.get_statistics()
    print(
        f"📊 Total uploads: "
        f"{stats.get('total_uploads', 0)}"
    )
    print(
        f"📅 Today's uploads: "
        f"{db.get_today_count()}/3"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()