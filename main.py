"""
Heavy Rain Deep Sleep - YouTube Automation
One part per trigger - stays under 6 hour limit
Random delay: 5-30 minutes
"""

import os
import sys
import time
import random
import glob
import json
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

# State file to track multi-part progress
STATE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "state.json"
)


def format_duration(seconds):
    hours   = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}h {minutes}m"


def humanize_start():
    """
    Random delay between 5-30 minutes
    """
    wait_minutes = random.randint(5, 30)
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

    time.sleep(wait_seconds)

    print(
        f"   ✅ Starting now: "
        f"{datetime.now().strftime('%H:%M:%S')}"
    )


def load_state():
    """
    Load multi-part state
    Tracks which part to upload next
    """
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return None


def save_state(state):
    """Save multi-part state"""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)


def clear_state():
    """Clear state after all parts done"""
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)


def main():
    print("=" * 60)
    print("🌧️  Heavy Rain Deep Sleep Automation")
    print(
        f"   Scheduled : "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print("   Mode      : Single part per trigger")
    print("=" * 60)

    # ── Humanize Start Time ──
    # Random delay between 5-30 minutes
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

    # ── Check for existing multi-part state ──
    state = load_state()

    if state:
        # ────────────────────────────────────
        # RESUME: Continue uploading next part
        # ────────────────────────────────────
        print("\n📋 Resuming multi-part upload...")
        print(
            f"   Audio     : {state['audio_name']}"
        )
        print(
            f"   Part      : "
            f"{state['next_part']}/"
            f"{state['total_parts']}"
        )
        print(
            f"   Title     : {state['ai_title']}"
        )

        audio_path     = state["audio_path"]
        audio_name     = state["audio_name"]
        audio_duration = state["audio_duration"]
        num_parts      = state["total_parts"]
        part_num       = state["next_part"]
        ai_title       = state["ai_title"]
        ai_desc        = state["ai_desc"]
        video_id       = state["video_id"]
        footage_url    = state.get("footage_url", "")

        # Re-download audio if not cached
        if not os.path.exists(audio_path):
            print(
                "\n📥 Re-downloading audio..."
            )
            audio_path, audio_name = (
                loader.download_random()
            )
            if not audio_path:
                print("❌ Audio re-download failed!")
                clear_state()
                sys.exit(1)

    else:
        # ────────────────────────────────────
        # NEW: Start fresh upload
        # ────────────────────────────────────
        print("\n🆕 Starting new upload...")

        # ── Load Random Audio ──
        print("\n📥 Loading random audio...")
        audio_path, audio_name = (
            loader.download_random()
        )
        if not audio_path:
            print("❌ Audio download failed!")
            sys.exit(1)

        print(f"   ✅ Using: {audio_name}")

        # ── Get Audio Duration ──
        print("\n⏱️ Checking audio duration...")
        audio_duration = processor.get_duration(
            audio_path
        )
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

        # ── Generate AI Metadata ──
        print("\n🤖 Generating AI metadata...")
        ai_title, ai_desc = ai.generate_metadata(
            audio_name, None, num_parts
        )
        print(f"   ✅ Title: {ai_title}")

        # ── Generate Unique Video ID ──
        video_id = (
            f"rain_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        # First part
        part_num    = 1
        footage_url = ""

        # ── Save State for future parts ──
        if num_parts > 1:
            print(
                f"\n📋 Multi-part video detected"
            )
            print(
                f"   Will upload part 1 now"
            )
            print(
                f"   Parts 2-{num_parts} in "
                f"next triggers"
            )

            save_state({
                "audio_path"    : audio_path,
                "audio_name"    : audio_name,
                "audio_duration": audio_duration,
                "total_parts"   : num_parts,
                "next_part"     : 2,
                "ai_title"      : ai_title,
                "ai_desc"       : ai_desc,
                "video_id"      : video_id,
                "footage_url"   : "",
            })

    # ════════════════════════════════════
    # PROCESS SINGLE PART
    # ════════════════════════════════════

    print(f"\n{'='*60}")
    print(
        f"🎬 Processing Part "
        f"{part_num}/{num_parts}"
    )
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
    print(
        f"   Duration: "
        f"{format_duration(part_duration)}"
    )

    # ── Get Stock Footage ──
    print("\n🎬 Getting stock footage...")
    footage_path = footage.get_footage()
    if not footage_path:
        print("❌ Footage download failed!")
        sys.exit(1)

    print(f"   ✅ Footage: {footage_path}")

    # ── Generate Thumbnail ──
    # Takes screenshot from the stock footage
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
        print("   ⚠️ Thumbnail failed")

    # ── Create Video ──
    print("\n🎥 Creating video...")
    print(
        f"   This may take "
        f"{int(part_duration/3600)}+ hours..."
    )
    part_output_id = (
        f"{video_id}_part{part_num}"
    )

    video_path = processor.create_video(
        audio_path     = audio_path,
        footage_path   = footage_path,
        output_id      = part_output_id,
        start_sec      = start_sec,
        end_sec        = end_sec,
        thumbnail_path = thumb_path
    )

    if not video_path:
        print("❌ Video creation failed!")
        sys.exit(1)

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
    print(f"\n📤 Uploading to YouTube...")
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
            f"\n   ✅ UPLOADED: "
            f"{result['url']}"
        )

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
        print(f"\n   ❌ Upload failed!")

    # ── Update state for next part ──
    if num_parts > 1:
        next_part = part_num + 1

        if next_part <= num_parts:
            # More parts remaining
            save_state({
                "audio_path"    : audio_path,
                "audio_name"    : audio_name,
                "audio_duration": audio_duration,
                "total_parts"   : num_parts,
                "next_part"     : next_part,
                "ai_title"      : ai_title,
                "ai_desc"       : ai_desc,
                "video_id"      : video_id,
                "footage_url"   : "",
            })
            print(
                f"\n📋 State saved: "
                f"Part {next_part}/{num_parts} "
                f"next trigger"
            )
        else:
            # All parts done
            clear_state()
            print(
                f"\n✅ All {num_parts} parts "
                f"uploaded!"
            )
    else:
        # Single video - no state needed
        clear_state()

    # ── Cleanup ──
    print("\n🧹 Cleaning up...")

    # Delete video file
    if video_path and os.path.exists(video_path):
        try:
            os.remove(video_path)
            print("   🗑️ Video deleted")
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
    for f in glob.glob("thumbnails/*.png"):
        try:
            os.remove(f)
        except Exception:
            pass
    print("   🗑️ Thumbnails deleted")

    # Do NOT delete audio if more parts remain
    state = load_state()
    if not state:
        # All parts done - delete audio
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
                print("   🗑️ Audio deleted")
            except Exception:
                pass

    # ── Summary ──
    print("\n" + "=" * 60)

    if result and result.get("success"):
        print(
            f"✅ Part {part_num}/{num_parts} "
            f"uploaded successfully!"
        )
        print(f"🔗 {result['url']}")
    else:
        print(
            f"❌ Part {part_num}/{num_parts} "
            f"failed"
        )

    stats = db.get_statistics()
    print(
        f"📊 Total all time : "
        f"{stats.get('total_uploads', 0)}"
    )
    print(
        f"📅 Today          : "
        f"{db.get_today_count()}/3"
    )

    remaining = load_state()
    if remaining:
        print(
            f"📋 Next trigger   : "
            f"Part {remaining['next_part']}/"
            f"{remaining['total_parts']}"
        )
    else:
        print(
            f"📋 Next trigger   : "
            f"New random audio"
        )

    print(
        f"🕐 Finished at    : "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
