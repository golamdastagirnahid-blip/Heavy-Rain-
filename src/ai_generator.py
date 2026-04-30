"""
AI Generator
SEO Optimized titles descriptions and tags
Heavy Rain Deep Sleep channel
"""

import os
import random
import requests


class AIGenerator:

    def __init__(self):
        self.api_key = os.getenv(
            "OPENROUTER_API_KEY", ""
        )
        self.model = (
            "mistralai/mistral-7b-instruct"
        )

    def generate_metadata(
        self,
        audio_name,
        part_num    = None,
        total_parts = None
    ):
        """
        Generate SEO optimized metadata
        Returns (title, description, tags)
        """
        print(
            "   🤖 Generating SEO metadata..."
        )

        title = self._title(
            audio_name, part_num, total_parts
        )
        desc  = self._description(
            title, part_num, total_parts
        )
        tags  = self._tags()

        print(f"   ✅ Title: {title}")
        print(f"   ✅ Tags : {len(tags)}")

        return title, desc, tags

    def _ai_call(self, prompt, max_tokens=100):
        """Make OpenRouter API call"""
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/"
                "chat/completions",
                headers={
                    "Authorization": (
                        f"Bearer {self.api_key}"
                    ),
                    "Content-Type": (
                        "application/json"
                    ),
                },
                json={
                    "model"   : self.model,
                    "messages": [{
                        "role"   : "user",
                        "content": prompt
                    }],
                    "max_tokens": max_tokens,
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json()[
                    "choices"
                ][0]["message"][
                    "content"
                ].strip()
        except Exception as e:
            print(f"   ⚠️ AI error: {e}")
        return None

    def _title(
        self,
        audio_name,
        part_num    = None,
        total_parts = None
    ):
        """SEO optimized title"""
        if self.api_key:
            result = self._ai_call(
                f"Write ONE YouTube title for heavy "
                f"rain deep sleep video.\n"
                f"Rules:\n"
                f"- Include Heavy Rain or Rain Sounds\n"
                f"- Include Sleep or Deep Sleep\n"
                f"- Add emojis\n"
                f"- Max 70 chars\n"
                f"- SEO keywords\n"
                f"- No quotes\n"
                f"- Only the title\n"
                f"Audio: {audio_name}",
                max_tokens=80
            )
            if result:
                result = result.strip('"\'')
                if (
                    part_num
                    and total_parts
                    and total_parts > 1
                ):
                    result = (
                        f"{result} "
                        f"| Part {part_num}"
                        f"/{total_parts}"
                    )
                return result

        return self._fallback_title(
            part_num, total_parts
        )

    def _description(
        self,
        title,
        part_num    = None,
        total_parts = None
    ):
        """SEO optimized description"""
        part_info = ""
        if (
            part_num
            and total_parts
            and total_parts > 1
        ):
            part_info = (
                f"\n📌 Part {part_num} "
                f"of {total_parts}\n"
            )

        if self.api_key:
            result = self._ai_call(
                f"Write YouTube description for "
                f"heavy rain deep sleep video.\n"
                f"Title: {title}\n"
                f"Rules:\n"
                f"- First line: engaging hook\n"
                f"- Include sleep benefits\n"
                f"- Call to action\n"
                f"- Max 300 words\n"
                f"- Natural tone\n"
                f"- SEO optimized\n"
                f"- Only description text",
                max_tokens=400
            )
            if result:
                return (
                    f"{result}"
                    f"{part_info}\n\n"
                    f"{self._hashtags()}"
                )

        return self._fallback_desc(
            title, part_info
        )

    def _tags(self):
        """Comprehensive SEO tags"""
        high = [
            "rain sounds",
            "sleep music",
            "white noise",
            "deep sleep",
            "relaxing music",
            "meditation music",
            "study music",
            "sleep sounds",
            "nature sounds",
            "ambient music",
        ]
        medium = [
            "heavy rain sounds",
            "rain sounds for sleeping",
            "rain sounds 8 hours",
            "rain on window",
            "thunderstorm sounds",
            "rain and thunder",
            "rain asmr",
            "sleep aid",
            "insomnia relief",
            "stress relief",
            "anxiety relief",
            "relaxation music",
            "focus music",
            "rain meditation",
            "heavy rainfall",
        ]
        niche = [
            "heavy rain deep sleep",
            "rain sounds no music",
            "rain sounds for studying",
            "heavy rain white noise",
            "deep sleep rain",
            "heavy rain meditation",
            "peaceful rain sounds",
            "gentle rain sounds",
            "rain sounds healing",
            "rain sounds focus",
            "storm sounds sleep",
            "rain forest sounds",
            "rain window sleep",
            "sleep instantly rain",
            "rain sounds babies",
        ]

        all_tags = high + medium + niche
        random.shuffle(all_tags)
        return all_tags[:30]

    def _hashtags(self):
        return (
            "#rainsounds #deepsleep #sleepmusic "
            "#heavyrain #whitenoise "
            "#rainsoundsforsleeping #sleepaid "
            "#insomnia #relaxingmusic "
            "#meditationmusic #studymusic "
            "#asmr #rainasmr #naturalsounds "
            "#stressrelief #anxietyrelief "
            "#focusmusic #ambientmusic "
            "#sleepsounds #rainonwindow "
            "#thunderstorm #heavyrainfall "
            "#sleepinstantly #deeprelaxation "
            "#mindfulness"
        )

    def _fallback_title(
        self,
        part_num    = None,
        total_parts = None
    ):
        titles = [
            "🌧️ Heavy Rain Sounds for Deep Sleep | 4 Hours No Ads",
            "⛈️ Thunderstorm & Heavy Rain | Deep Sleep White Noise",
            "🌧️ Heavy Rain on Window | Fall Asleep Fast Tonight",
            "⛈️ Heavy Rainfall Sounds | Deep Sleep & Relaxation",
            "🌧️ Rain Sounds for Sleeping | Heavy Rain 4 Hours",
            "🌧️ Heavy Rain White Noise | Sleep Instantly Tonight",
            "⛈️ Powerful Rain & Thunder | Deep Sleep Sounds",
            "🌧️ All Night Heavy Rain | Sleep Sounds No Ads",
            "🌧️ Heavy Rain ASMR | Deep Sleep White Noise",
            "⛈️ Intense Rain | Insomnia Relief No Ads",
        ]
        title = random.choice(titles)
        if (
            part_num
            and total_parts
            and total_parts > 1
        ):
            title = (
                f"{title} "
                f"| Part {part_num}/{total_parts}"
            )
        return title

    def _fallback_desc(self, title, part_info):
        return f"""🌧️ {title}
{part_info}
Experience the ultimate deep sleep with our heavy rain sounds. This powerful rain audio helps you fall asleep fast, stay asleep longer, and wake up refreshed.

💤 WHY HEAVY RAIN WORKS FOR SLEEP:
Heavy rain creates consistent white noise that blocks distracting sounds. The steady rhythm triggers your brain's relaxation response, lowering cortisol and preparing your body for deep restorative sleep.

✅ PERFECT FOR:
• Deep Sleep & Insomnia Relief
• Study & Focus Sessions
• Meditation & Mindfulness
• Stress & Anxiety Relief
• Baby Sleep & Nap Time
• Background Noise for Work
• ASMR Relaxation

🎯 BENEFITS:
→ Fall asleep up to 3x faster
→ Blocks background noise naturally
→ Reduces stress and anxiety
→ Improves sleep quality
→ No music, no interruptions, no ads

🔔 SUBSCRIBE for daily rain sounds!
👍 LIKE if this helped you sleep!
💬 COMMENT your favorite rain sound!

{self._hashtags()}"""
