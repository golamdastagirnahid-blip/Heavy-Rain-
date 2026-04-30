"""
AI Generator
SEO Optimized titles, descriptions and tags
Engaging and keyword rich content
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
        Returns (title, description)
        """
        print("   🤖 Generating SEO metadata...")

        title = self._generate_title(
            audio_name, part_num, total_parts
        )
        desc  = self._generate_description(
            title, part_num, total_parts
        )
        tags  = self._generate_tags()

        print(f"   ✅ Title: {title}")
        print(f"   ✅ Tags : {len(tags)} tags")

        return title, desc, tags

    def _generate_title(
        self,
        audio_name,
        part_num    = None,
        total_parts = None
    ):
        """Generate SEO optimized YouTube title"""

        if self.api_key:
            try:
                prompt = (
                    f"Generate ONE YouTube title for a "
                    f"heavy rain deep sleep video. "
                    f"Rules:\n"
                    f"- Must include: 'Heavy Rain' or "
                    f"'Rain Sounds'\n"
                    f"- Must include: 'Sleep' or "
                    f"'Deep Sleep'\n"
                    f"- Add relevant emojis\n"
                    f"- SEO friendly keywords\n"
                    f"- Max 70 characters\n"
                    f"- No quotes in response\n"
                    f"- Only return the title\n"
                    f"Audio: {audio_name}"
                )

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
                        "max_tokens": 80,
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    title = response.json()[
                        "choices"
                    ][0]["message"][
                        "content"
                    ].strip()
                    title = title.strip('"\'')

                    # Add part if needed
                    if (
                        part_num
                        and total_parts
                        and total_parts > 1
                    ):
                        title = (
                            f"{title} "
                            f"| Part {part_num}"
                            f"/{total_parts}"
                        )
                    return title

            except Exception as e:
                print(f"   ⚠️ AI title error: {e}")

        return self._fallback_title(
            part_num, total_parts
        )

    def _generate_description(
        self,
        title,
        part_num    = None,
        total_parts = None
    ):
        """
        Generate SEO optimized description
        Keyword rich and engaging
        """
        if self.api_key:
            try:
                prompt = (
                    f"Write a YouTube description for "
                    f"a heavy rain deep sleep video.\n"
                    f"Title: {title}\n"
                    f"Rules:\n"
                    f"- First 2 lines must be engaging "
                    f"and keyword rich\n"
                    f"- Include sleep benefits\n"
                    f"- Include call to action\n"
                    f"- Add hashtags at end\n"
                    f"- Max 400 words\n"
                    f"- Natural human tone\n"
                    f"- SEO optimized\n"
                    f"- Only return description"
                )

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
                        "max_tokens": 500,
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    ai_desc = response.json()[
                        "choices"
                    ][0]["message"][
                        "content"
                    ].strip()

                    # Add part info
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

                    return (
                        f"{ai_desc}"
                        f"{part_info}"
                    )

            except Exception as e:
                print(f"   ⚠️ AI desc error: {e}")

        return self._fallback_description(
            title, part_num, total_parts
        )

    def _generate_tags(self):
        """
        Generate comprehensive SEO tags
        Mix of high volume and niche tags
        """
        # High volume tags
        high_volume = [
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

        # Medium volume tags
        medium = [
            "heavy rain sounds",
            "rain sounds for sleeping",
            "rain sounds 8 hours",
            "rain sounds 10 hours",
            "rain on window",
            "thunderstorm sounds",
            "rain and thunder",
            "rain asmr",
            "sleep aid",
            "insomnia relief",
            "stress relief music",
            "anxiety relief",
            "relaxation music",
            "focus music",
            "rain meditation",
        ]

        # Niche/long tail tags
        niche = [
            "heavy rain deep sleep",
            "rain sounds no music",
            "rain sounds for studying",
            "rain sounds for anxiety",
            "heavy rain white noise",
            "rain sounds sleep aid",
            "deep sleep rain sounds",
            "heavy rain meditation",
            "rain sounds relaxation",
            "peaceful rain sounds",
            "gentle rain sounds",
            "rain sounds for babies",
            "rain sounds for dogs",
            "rain forest sounds",
            "rain window sleep",
            "storm sounds sleep",
            "heavy rainfall sounds",
            "rain sounds healing",
            "rain sounds focus",
            "rain sounds study",
        ]

        # Combine all tags
        all_tags = (
            high_volume + medium + niche
        )

        # Shuffle for variety
        random.shuffle(all_tags)

        # YouTube allows max 500 chars in tags
        # Return up to 30 tags
        return all_tags[:30]

    def _fallback_title(
        self,
        part_num    = None,
        total_parts = None
    ):
        """High quality fallback titles"""
        titles = [
            "🌧️ Heavy Rain Sounds for Deep Sleep | 4 Hours No Ads",
            "⛈️ Thunderstorm & Heavy Rain for Deep Sleep | White Noise",
            "🌧️ Heavy Rain on Window for Sleep | 4 Hours No Music",
            "⛈️ Heavy Rainfall Sounds | Deep Sleep & Relaxation",
            "🌧️ Rain Sounds for Sleeping | Heavy Rain No Ads 4 Hours",
            "🌧️ Heavy Rain White Noise | Fall Asleep Fast Tonight",
            "⛈️ Powerful Rain & Thunder Sounds for Deep Sleep",
            "🌧️ All Night Heavy Rain Sounds | Sleep Instantly",
            "🌧️ Heavy Rain ASMR | Deep Sleep White Noise 4 Hours",
            "⛈️ Intense Rain Sounds for Insomnia Relief | No Ads",
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

    def _fallback_description(
        self,
        title,
        part_num    = None,
        total_parts = None
    ):
        """
        High quality SEO optimized
        fallback description
        """
        part_info = ""
        if (
            part_num
            and total_parts
            and total_parts > 1
        ):
            part_info = (
                f"📌 Part {part_num} "
                f"of {total_parts}\n\n"
            )

        desc = f"""🌧️ {title}

{part_info}Experience the ultimate deep sleep with our heavy rain sounds. This powerful rain audio is carefully recorded to help you fall asleep fast, stay asleep longer, and wake up feeling completely refreshed.

💤 WHY HEAVY RAIN SOUNDS WORK FOR SLEEP:
Heavy rain creates a consistent white noise that naturally blocks out distracting sounds. The steady rhythm of rainfall triggers your brain's relaxation response, lowering cortisol levels and preparing your body for deep, restorative sleep.

✅ PERFECT FOR:
• Deep Sleep & Insomnia Relief
• Study & Focus Sessions
• Meditation & Mindfulness
• Stress & Anxiety Relief
• Yoga & Relaxation
• Baby Sleep & Nap Time
• Background Noise for Work
• ASMR Relaxation

🎯 SLEEP BENEFITS:
→ Falls asleep up to 3x faster
→ Blocks disruptive background noise
→ Reduces stress and anxiety
→ Improves sleep quality naturally
→ No music, no interruptions, no ads

🔔 SUBSCRIBE for daily rain sounds and sleep music uploads!
👍 LIKE this video if it helped you sleep!
💬 COMMENT below which rain sound works best for you!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

#rainsounds #deepsleep #sleepmusic #heavyrain #whitenoise #rainsoundsforsleepin #sleepaid #insomnia #relaxingmusic #meditationmusic #studymusic #asmr #rainasmr #naturalsounds #stressrelief #anxietyrelief #focusmusic #ambientmusic #sleepsounds #rainonwindow #thunderstorm #rainthunder #heavyrainfall #sleepinstantly #deeprelaxation #mindfulness #calmmusic #peacefulmusic #insomniarelief #babysleep"""

        return desc
