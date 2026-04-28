"""
Heavy Rain Deep Sleep - YouTube Automation
Main entry point
Picks random audio from Google Drive folder
Gets stock footage from Pexels/Pixabay
Loops footage over audio
Uploads to YouTube
Humanized upload times (1-90 min random delay)
"""

import os
import sys
import time
import random
import glob
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


def humanize_start():
    """
    Wait a random time before starting
    Makes upload times look natural
    Between 1 and 90 minutes random delay
    """
    wait_minutes = random.randint(1, 90)
    wait_seconds = wait_minutes * 60

    print(f"⏰ Humanizing start time...")
    print(
        f"   Random delay  : "
        f"{wait_minutes} minutes"
    )
    print(
        f"   Current time  : "
        f"{datetime.now().strftime('%H:%M:%S')}"
    )
    print(
        f"   Will start at : "
        f"{wait_minutes} min from now"
    )

    time.sleep(wait_seconds)

    print(
        f"   ✅ Starting now: "
        f"{datetime.now().strftime('%H:%M:%S')}"
    )


def main():
    print("=" * 60)
    print("🌧️  Heavy Rain Deep Sleep Automation")
    print(
        f"   Scheduled : "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print("=" * 60)

    # ── Humanize Start Time ──
    # Random delay between 1-90 minutes
    humanize_start()

    print(
        f"\n🕐 Actual start: "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # ── Initialize Components ──
    db        = Database()
    loader    = AudioLoader()
    footage   = FootageDownloader()
    processor = VideoProcessor()
    ai        = AIGenerator()
    thumb_gen = ThumbnailGenerator()
    auth      = YouTubeAuth()

    # ── Check Daily Limit ──
    today_count = db.get_today_count()
    print(f"\n📊 Today's uploads: {today_count}/3")

    if today_count >= 3:
        print("✅ Daily limit reached (3 videos)")
        print("   Will resume tomorrow")
        return

    # ── Authenticate YouTube ──
    youtube = auth.authenticate()
    if not youtube:
        print("❌ YouTube authentication failed!")
        sys.exit(1)

    uploader = VideoUploader(youtube)

    # ── Load Random Audio ──
    print("\n📥 Loading random audio...")
    audio_path, audio_name = loader.download_random()
    if not audio_path:
        print("❌ Audio download failed!")
        sys.exit(1)

    print(f"   ✅ Using: {audio_name}")

    # ── Get Audio Duration ──
    print("\n⏱️ Checking audio duration...")
    audio_duration = processor.get_duration(audio_path)
    if audio_duration == 0:
        print("❌ Could not get audio duration!")
        sys.exit(1)

    print(
        f"   Duration: "
        f"{format_duration(audio_duration)}"
    )

    # ── Calculate Parts ──
    num_parts = processor.calculate_parts(
        audio_duration
    )
    print(f"   Parts   : {num_parts}")

    # ── Get Stock Footage ──
    print("\n🎬 Getting stock footage...")
    footage_path = footage.get_footage()
    if not footage_path:
        print("❌ Footage download failed!")
        sys.exit(1)

    print(f"   ✅ Footage: {footage_path}")

    # ── Generate Unique Video ID ──
    video_id = (
        f"rain_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

    # ── Generate AI Metadata ──
    print("\n🤖 Generating AI metadata...")
    ai_title, ai_desc = ai.generate_metadata(
        audio_name, None, num_parts
    )
    print(f"   ✅ Title: {ai_title}")

    # ── Process Each Part ──
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
            f"   ⏱️  "
            f"{format_duration(start_sec)} → "
            f"{format_duration(end_sec)}"
        )

        # ── Generate Thumbnail ──
        print("\n🖼️ Generating thumbnail...")
        thumb_path = thumb_gen.generate(
            title        = ai_title,
            footage_path = footage_path,
            part_num     = part_num
                           if num_parts > 1
                           else None,
            total_parts  = num_parts
                           if num_parts > 1
                           else None,
            duration_str = format_duration(
                part_duration
            )
        )

        if not thumb_path:
            print("   ⚠️ Thumbnail failed - continuing")

        # ── Create Video ──
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

        print(f"   ✅ Video: {video_path}")

        # ── Build Title & Description ──
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

        # ── Upload to YouTube ──
        print(f"\n📤 Uploading Part {part_num}...")
        print(
            f"   Title: {part_title[:60]}..."
            if len(part_title) > 60
            else f"   Title: {part_title}"
        )

        result = uploader.upload(
            video_path     = video_path,
            title          = part_title,
            description    = part_desc,
            thumbnail_path = thumb_path,
            privacy        = "public",
        )

        if result and result.get("success"):
            print(
                f"   ✅ Uploaded: "
                f"{result['url']}"
            )
            success_count += 1

            # Mark in database
            db.mark_uploaded(
                f"{part_output_id}",
                {
                    "title"  : part_title,
                    "url"    : result["url"],
                    "audio"  : audio_name,
                    "part"   : part_num,
                    "of"     : num_parts,
                }
            )
        else:
            print(f"   ❌ Part {part_num} upload failed")

        # ── Cleanup Part Video ──
        if video_path and os.path.exists(video_path):
            try:
                os.remove(video_path)
                print("   🗑️ Part video deleted")
            except Exception:
                pass

        # ── Humanized Wait Between Parts ──
        if part_num < num_parts:
            wait = random.randint(60, 300)
            print(
                f"\n⏳ Waiting "
                f"{wait // 60}m {wait % 60}s "
                f"before next part..."
            )
            time.sleep(wait)

    # ── Final Cleanup ──
    print("\n🧹 Final cleanup...")

    # Delete audio
    if audio_path and os.path.exists(audio_path):
        try:
            os.remove(audio_path)
            print("   🗑️ Audio deleted")
        except Exception:
            pass

    # Delete footage
    if footage_path and os.path.exists(footage_path):
        try:
            os.remove(footage_path)
            print("   🗑️ Footage deleted")
        except Exception:
            pass

    # Delete thumbnails
    for f in glob.glob("thumbnails/*.jpg"):
        try:
            os.remove(f)
        except Exception:
            pass
    print("   🗑️ Thumbnails deleted")

    # Delete temp frames
    for f in glob.glob("thumbnails/*.png"):
        try:
            os.remove(f)
        except Exception:
            pass

    # ── Final Summary ──
    print("\n" + "=" * 60)
    print(
        f"✅ Done! "
        f"{success_count}/{num_parts} parts uploaded"
    )
    stats = db.get_statistics()
    print(
        f"📊 Total all time : "
        f"{stats.get('total_uploads', 0)} videos"
    )
    print(
        f"📅 Today          : "
        f"{db.get_today_count()}/3 videos"
    )
    print(
        f"🕐 Finished at    : "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
