"""
Heavy Rain Deep Sleep - YouTube Automation
ONE PART PER TRIGGER
Remembers audio cut position between triggers
Random delay: 5-30 minutes
High quality audio: 192k
720p video output
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


MAX_PART_SECONDS = 4 * 60 * 60

STATE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "state.json"
)


def format_duration(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    return f"{h}h {m}m"


def humanize_start():
    """Random delay 5-30 minutes"""
    wait = random.randint(5, 30)
    print(f"⏰ Random delay: {wait} minutes")
    print(
        f"   Start time: "
        f"{datetime.now().strftime('%H:%M:%S')}"
    )
    time.sleep(wait * 60)
    print(
        f"   ✅ Running now: "
        f"{datetime.now().strftime('%H:%M:%S')}"
    )


def load_state():
    """Load saved state from previous trigger"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return None


def save_state(state):
    """Save state for next trigger"""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)
    print(f"   💾 State saved")


def clear_state():
    """Clear state when all parts done"""
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    print("   🗑️ State cleared")


def main():
    print("=" * 60)
    print("🌧️  Heavy Rain Deep Sleep Bot")
    print(
        f"   Time: "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print("   Mode: 1 Part Per Trigger")
    print("=" * 60)

    # ── Random delay 5-30 min ──
    humanize_start()

    print(
        f"\n🕐 Actual start: "
        f"{datetime.now().strftime('%H:%M:%S')}"
    )

    # ── Init ──
    db        = Database()
    loader    = AudioLoader()
    footage   = FootageDownloader()
    processor = VideoProcessor()
    ai        = AIGenerator()
    thumb_gen = ThumbnailGenerator()
    auth      = YouTubeAuth()

    # ── Daily limit check ──
    today_count = db.get_today_count()
    print(f"\n📊 Today: {today_count}/3 uploads")

    if today_count >= 3:
        print("✅ Daily limit reached")
        return

    # ── Auth YouTube ──
    youtube = auth.authenticate()
    if not youtube:
        print("❌ Auth failed!")
        sys.exit(1)

    uploader = VideoUploader(youtube)

    # ════════════════════════════════════
    # CHECK STATE - Resume or Start Fresh
    # ════════════════════════════════════

    state = load_state()

    if state:
        # ── RESUME: Upload next part ──
        print("\n📋 Resuming multi-part upload")
        print(
            f"   Audio   : {state['audio_name']}"
        )
        print(
            f"   Part    : "
            f"{state['current_part']}/"
            f"{state['total_parts']}"
        )
        print(
            f"   Title   : {state['ai_title']}"
        )
        print(
            f"   Cut at  : "
            f"{format_duration(state['start_sec'])}"
        )

        audio_path     = state["audio_path"]
        audio_file_id  = state["audio_file_id"]
        audio_name     = state["audio_name"]
        audio_duration = state["audio_duration"]
        total_parts    = state["total_parts"]
        current_part   = state["current_part"]
        start_sec      = state["start_sec"]
        end_sec        = state["end_sec"]
        ai_title       = state["ai_title"]
        ai_desc        = state["ai_desc"]
        ai_tags        = state["ai_tags"]
        video_id       = state["video_id"]

        # Re-download audio if not cached
        if not os.path.exists(audio_path):
            print(
                "\n📥 Re-downloading audio..."
            )
            audio_path = loader.download_by_id(
                audio_file_id, audio_name
            )
            if not audio_path:
                print(
                    "❌ Audio re-download failed!"
                )
                clear_state()
                sys.exit(1)

    else:
        # ── NEW: Fresh start ──
        print("\n🆕 Starting new audio...")

        # Download random audio
        print("\n📥 Loading random audio...")
        audio_path, audio_file_id, audio_name = (
            loader.download_random()
        )
        if not audio_path:
            print("❌ Audio download failed!")
            sys.exit(1)

        print(f"   ✅ Audio: {audio_name}")

        # Get duration
        print("\n⏱️ Getting duration...")
        audio_duration = processor.get_duration(
            audio_path
        )
        if audio_duration == 0:
            print("❌ Duration failed!")
            sys.exit(1)

        print(
            f"   Duration: "
            f"{format_duration(audio_duration)}"
        )

        # Calculate parts
        total_parts = processor.calculate_parts(
            audio_duration
        )
        print(f"   Parts   : {total_parts}")

        # First part starts at 0
        current_part = 1
        start_sec    = 0
        end_sec      = min(
            MAX_PART_SECONDS, audio_duration
        )

        # Generate video ID
        video_id = (
            f"rain_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        # Generate AI metadata once
        # (same title/desc/tags for all parts)
        print("\n🤖 Generating SEO metadata...")
        ai_title, ai_desc, ai_tags = (
            ai.generate_metadata(
                audio_name, None, total_parts
            )
        )

    # ════════════════════════════════════
    # PROCESS SINGLE PART
    # ════════════════════════════════════

    part_duration = end_sec - start_sec

    print(f"\n{'='*60}")
    print(
        f"🎬 Processing Part "
        f"{current_part}/{total_parts}"
    )
    print(f"{'='*60}")
    print(
        f"   Cut    : "
        f"{format_duration(start_sec)} → "
        f"{format_duration(end_sec)}"
    )
    print(
        f"   Length : "
        f"{format_duration(part_duration)}"
    )

    # ── Get footage ──
    print("\n🎬 Getting stock footage...")
    footage_path = footage.get_footage()
    if not footage_path:
        print("❌ Footage failed!")
        sys.exit(1)

    print(f"   ✅ Footage ready")

    # ── Generate thumbnail ──
    print("\n🖼️ Generating thumbnail...")
    thumb_path = thumb_gen.generate(
        title        = ai_title,
        footage_path = footage_path,
        part_num     = current_part
                       if total_parts > 1
                       else None,
        total_parts  = total_parts
                       if total_parts > 1
                       else None,
        duration_str = format_duration(
            part_duration
        )
    )

    # ── Create video ──
    print("\n🎥 Creating video...")
    part_output_id = (
        f"{video_id}_p{current_part}"
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

    print(f"   ✅ Video ready")

    # ── Build title & description ──
    if total_parts > 1:
        part_title = (
            f"{ai_title} "
            f"| Part {current_part}/{total_parts}"
        )
    else:
        part_title = ai_title

    part_desc = (
        f"{ai_desc}\n\n"
        f"⏱️ Duration: "
        f"{format_duration(part_duration)}\n"
    )
    if total_parts > 1:
        part_desc += (
            f"📌 Part {current_part} "
            f"of {total_parts}\n"
        )

    # ── Upload ──
    print(f"\n📤 Uploading to YouTube...")
    print(f"   Title: {part_title}")

    result = uploader.upload(
        video_path     = video_path,
        title          = part_title,
        description    = part_desc,
        tags           = ai_tags,
        thumbnail_path = thumb_path,
        privacy        = "public",
    )

    if result and result.get("success"):
        print(
            f"\n✅ UPLOADED: {result['url']}"
        )
        db.mark_uploaded(
            part_output_id,
            {
                "title"  : part_title,
                "url"    : result["url"],
                "audio"  : audio_name,
                "part"   : current_part,
                "of"     : total_parts,
            }
        )
    else:
        print("\n❌ Upload failed!")

    # ════════════════════════════════════
    # SAVE STATE FOR NEXT TRIGGER
    # ════════════════════════════════════

    next_part  = current_part + 1
    next_start = end_sec
    next_end   = min(
        next_start + MAX_PART_SECONDS,
        audio_duration
    )

    if next_part <= total_parts:
        # More parts remaining
        # Save position for next trigger
        save_state({
            "audio_path"    : audio_path,
            "audio_file_id" : audio_file_id,
            "audio_name"    : audio_name,
            "audio_duration": audio_duration,
            "total_parts"   : total_parts,
            "current_part"  : next_part,
            "start_sec"     : next_start,
            "end_sec"       : next_end,
            "ai_title"      : ai_title,
            "ai_desc"       : ai_desc,
            "ai_tags"       : ai_tags,
            "video_id"      : video_id,
        })
        print(
            f"\n📋 Next trigger: "
            f"Part {next_part}/{total_parts}"
        )
        print(
            f"   Will cut from: "
            f"{format_duration(next_start)}"
        )
    else:
        # All parts done
        clear_state()
        # Delete audio - fully processed
        if audio_path and os.path.exists(
            audio_path
        ):
            try:
                os.remove(audio_path)
                print("   🗑️ Audio deleted")
            except Exception:
                pass
        print("\n✅ All parts complete!")

    # ── Cleanup ──
    print("\n🧹 Cleanup...")

    if video_path and os.path.exists(video_path):
        try:
            os.remove(video_path)
            print("   🗑️ Video deleted")
        except Exception:
            pass

    if footage_path and os.path.exists(
        footage_path
    ):
        try:
            os.remove(footage_path)
            print("   🗑️ Footage deleted")
        except Exception:
            pass

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

    # ── Summary ──
    print("\n" + "="*60)
    print(
        f"✅ Part {current_part}/{total_parts} done"
    )
    if result and result.get("success"):
        print(f"🔗 {result['url']}")
    stats = db.get_statistics()
    print(
        f"📊 Total: "
        f"{stats.get('total_uploads',0)}"
    )
    print(
        f"📅 Today: {db.get_today_count()}/3"
    )

    remaining = load_state()
    if remaining:
        print(
            f"⏭️  Next: Part "
            f"{remaining['current_part']}/"
            f"{remaining['total_parts']} "
            f"@ {format_duration(remaining['start_sec'])}"
        )
    else:
        print("⏭️  Next: New random audio")

    print(
        f"🕐 Done: "
        f"{datetime.now().strftime('%H:%M:%S')}"
    )
    print("="*60)


if __name__ == "__main__":
    main()
