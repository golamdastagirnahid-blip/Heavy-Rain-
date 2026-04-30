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
                f"\nPart {part_num} "
                f"of {total_parts}\n"
            )

        if self.api_key:
            result = self._ai_call(
                f"Write YouTube description for "
                f"heavy rain deep sleep video.\n"
                f"Title: {title}\n"
                f"Rules:\n"
                f"- First line engaging hook\n"
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
        """
        YouTube safe tags
        No special characters
        No quotes
        No angle brackets
        Max 500 chars total
        Each tag max 30 chars
        """
        tags = [
            "rain sounds",
            "deep sleep",
            "heavy rain",
            "sleep music",
            "white noise",
            "rain sounds for sleeping",
            "heavy rain sounds",
            "sleep aid",
            "insomnia relief",
            "relaxing rain",
            "rain asmr",
            "nature sounds",
            "ambient sounds",
            "study music",
            "meditation music",
            "thunderstorm sounds",
            "rain and thunder",
            "sleep sounds",
            "stress relief",
            "anxiety relief",
            "focus music",
            "relaxation music",
            "rain on window",
            "heavy rainfall",
            "peaceful rain",
            "gentle rain sounds",
            "rain meditation",
            "sleep instantly",
            "deep relaxation",
            "rain white noise",
        ]

        # Validate each tag
        clean_tags = []
        total_chars = 0

        for tag in tags:
            # Remove any special characters
            clean = tag.strip()
            clean = clean.replace('"', '')
            clean = clean.replace("'", '')
            clean = clean.replace('<', '')
            clean = clean.replace('>', '')
            clean = clean.replace('&', 'and')

            # YouTube tag limits
            if len(clean) > 30:
                clean = clean[:30]

            if not clean:
                continue

            # YouTube total tags limit 500 chars
            if total_chars + len(clean) + 1 > 490:
                break

            clean_tags.append(clean)
            total_chars += len(clean) + 1

        return clean_tags

    def _hashtags(self):
        """Plain text hashtags for description"""
        return (
            "#rainsounds #deepsleep #sleepmusic "
            "#heavyrain #whitenoise "
            "#sleepaid #insomnia "
            "#relaxingmusic #meditationmusic "
            "#studymusic #rainasmr "
            "#naturalsounds #stressrelief "
            "#anxietyrelief #focusmusic "
            "#ambientmusic #sleepsounds "
            "#rainonwindow #thunderstorm "
            "#heavyrainfall #deeprelaxation "
            "#mindfulness #calmmusic"
        )

    def _fallback_title(
        self,
        part_num    = None,
        total_parts = None
    ):
        """High quality fallback titles"""
        titles = [
            "Heavy Rain Sounds for Deep Sleep 4 Hours No Ads",
            "Thunderstorm Heavy Rain Deep Sleep White Noise",
            "Heavy Rain on Window Fall Asleep Fast Tonight",
            "Heavy Rainfall Sounds Deep Sleep Relaxation",
            "Rain Sounds for Sleeping Heavy Rain 4 Hours",
            "Heavy Rain White Noise Sleep Instantly Tonight",
            "Powerful Rain and Thunder Deep Sleep Sounds",
            "All Night Heavy Rain Sleep Sounds No Ads",
            "Heavy Rain ASMR Deep Sleep White Noise",
            "Intense Rain Insomnia Relief No Ads",
        ]
        title = random.choice(titles)
        if (
            part_num
            and total_parts
            and total_parts > 1
        ):
            title = (
                f"{title} "
                f"Part {part_num} of {total_parts}"
            )
        return title

    def _fallback_desc(self, title, part_info):
        """High quality SEO description"""
        return (
            f"{title}\n"
            f"{part_info}\n"
            f"Experience the ultimate deep sleep "
            f"with our heavy rain sounds. "
            f"This powerful rain audio helps you "
            f"fall asleep fast, stay asleep longer, "
            f"and wake up completely refreshed.\n\n"
            f"WHY HEAVY RAIN WORKS FOR SLEEP:\n"
            f"Heavy rain creates consistent white "
            f"noise that blocks distracting sounds. "
            f"The steady rhythm triggers your brain "
            f"relaxation response, lowering cortisol "
            f"and preparing your body for deep "
            f"restorative sleep.\n\n"
            f"PERFECT FOR:\n"
            f"Deep Sleep and Insomnia Relief\n"
            f"Study and Focus Sessions\n"
            f"Meditation and Mindfulness\n"
            f"Stress and Anxiety Relief\n"
            f"Baby Sleep and Nap Time\n"
            f"Background Noise for Work\n"
            f"ASMR Relaxation\n\n"
            f"BENEFITS:\n"
            f"Fall asleep up to 3x faster\n"
            f"Blocks background noise naturally\n"
            f"Reduces stress and anxiety\n"
            f"Improves sleep quality\n"
            f"No music no interruptions no ads\n\n"
            f"Subscribe for daily rain sounds!\n"
            f"Like if this helped you sleep!\n"
            f"Comment your favorite rain sound!\n\n"
            f"{self._hashtags()}"
        )
