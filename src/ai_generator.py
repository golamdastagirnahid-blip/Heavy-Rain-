"""
AI Generator
SEO Optimized titles descriptions and tags
High search volume keywords
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
                f"- Add 1-2 emojis\n"
                f"- Max 70 chars\n"
                f"- Use high search volume keywords\n"
                f"- No quotes\n"
                f"- Only return the title\n"
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
                f"- First 2 lines must be engaging\n"
                f"- Include sleep benefits\n"
                f"- Include call to action\n"
                f"- Use keywords: rain sounds, "
                f"deep sleep, white noise, "
                f"sleep music, insomnia relief\n"
                f"- Max 300 words\n"
                f"- Natural human tone\n"
                f"- Only return description text",
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
        High search volume YouTube tags
        From provided SEO keyword list
        Only safe characters
        No special symbols
        Max 30 chars each
        Total max 490 chars
        Rotates randomly each upload
        """

        # All provided high volume keywords
        # Cleaned and safe for YouTube API
        all_keywords = [
            "rain sounds",
            "rain sounds for sleeping",
            "rain sounds for sleep",
            "heavy rain sounds",
            "rain sound for sleeping",
            "relaxing rain sounds",
            "sleep sounds",
            "thunder and rain sounds",
            "rain and thunder",
            "white noise",
            "rain on window",
            "rain sounds for studying",
            "gentle rain",
            "sleep music",
            "rain for sleeping",
            "help insomnia",
            "sleep",
            "rain asmr",
            "soothing rain",
            "heavy rain",
            "rain and thunder sounds",
            "thunderstorm sounds",
            "rain sounds to sleep",
            "soft rain",
            "rain to sleep",
            "rain for sleep",
            "deep sleep",
            "relaxing rain",
            "sleep instantly",
            "insomnia",
            "sleep sound",
            "white noise for sleeping",
            "beat insomnia",
            "rain",
            "thunderstorm",
            "sleeping",
            "heavy rain and thunder",
            "the sound of rain",
            "rainstorm sounds",
            "sleep noise",
            "rain no thunder",
            "stress relief",
            "white noise rain",
            "rain at night",
            "rain sleep",
            "ambience",
            "sounds of rain",
            "white noise for sleep",
            "sound of rain",
            "light rain",
            "rainforest sounds",
            "rain window",
            "sleeping sounds",
            "help sleeping",
            "relaxing",
            "tinnitus relief",
            "soothing music",
            "relaxing sounds",
            "fall asleep fast",
            "heavy rain for sleep",
            "rain 10 hours",
            "natural white noise",
            "sleep disorders",
            "tranquil music",
            "sleeping music",
            "storm sounds",
            "insomnia symptoms",
            "night rain",
            "strong rain",
            "rain storm",
            "anxiety relief",
            "storm",
            "study sounds",
            "rain sleeping sounds",
            "sleep music no ads",
            "relaxing music",
            "sounds for sleep",
            "water sounds for sleeping",
            "sleeping music",
            "music for sleeping",
            "white noise sleep",
            "rain falling sounds",
            "relax",
            "study",
            "relaxation music",
            "cozy cabin",
            "rain thunder",
            "rain noise",
            "rain drops",
            "raining sounds",
            "rain thunderstorm",
            "relax music",
            "jungle rain",
            "strong thunderstorm",
            "rain ambience",
            "water sounds",
            "window rain",
            "sleep rain",
            "heavy thunder",
            "relaxation meditation",
            "thunderstorm for sleep",
            "heavy rain at night",
            "thunder sounds sleep",
            "thunderstorm for sleeping",
            "rain sound",
        ]

        # Always include these top priority tags
        priority = [
            "rain sounds",
            "rain sounds for sleeping",
            "heavy rain sounds",
            "deep sleep",
            "white noise",
            "sleep music",
            "rain asmr",
            "thunderstorm sounds",
            "sleep sounds",
            "insomnia relief",
        ]

        # Pick remaining from full list randomly
        remaining = [
            k for k in all_keywords
            if k not in priority
        ]
        random.shuffle(remaining)

        # Combine priority + random selection
        selected = priority + remaining

        # Build final tag list
        # Respect YouTube limits
        final = []
        total = 0

        for tag in selected:
            # Clean tag
            t = tag.strip().lower()

            # Skip if too short
            if len(t) < 2:
                continue

            # Enforce max 30 chars
            if len(t) > 30:
                t = t[:30].strip()

            # Skip duplicates
            if t in final:
                continue

            # YouTube 500 char total limit
            # Each tag costs len + 1 for comma
            if total + len(t) + 1 > 490:
                break

            final.append(t)
            total += len(t) + 1

            # YouTube max ~30 tags practical limit
            if len(final) >= 30:
                break

        print(
            f"   📊 Tags: {len(final)} tags "
            f"/ {total} chars"
        )

        return final

    def _hashtags(self):
        """
        High search volume hashtags
        For video description
        """
        return (
            "#rainsounds #deepsleep #sleepmusic "
            "#heavyrain #whitenoise "
            "#rainsoundsforsleepin #sleepaid "
            "#insomnia #relaxingmusic "
            "#meditationmusic #studymusic "
            "#rainasmr #naturalsounds "
            "#stressrelief #anxietyrelief "
            "#focusmusic #ambientmusic "
            "#sleepsounds #thunderstorm "
            "#heavyrainfall #deeprelaxation "
            "#mindfulness #calmmusic "
            "#rainonwindow #whitenoisesleep "
            "#insomniarelief #sleepinstantly "
            "#rainandthunder #naturalsounds "
            "#relaxation"
        )

    def _fallback_title(
        self,
        part_num    = None,
        total_parts = None
    ):
        """
        High search volume fallback titles
        Using provided keywords
        """
        titles = [
            "🌧️ Heavy Rain Sounds for Deep Sleep | Black Screen No Ads",
            "⛈️ Rain Sounds for Sleeping | Heavy Rain White Noise",
            "🌧️ Heavy Rain and Thunder Sounds for Deep Sleep",
            "🌧️ Rain Sounds for Sleep | Thunderstorm White Noise",
            "⛈️ Heavy Rain Sounds | Fall Asleep Fast No Ads",
            "🌧️ Rain on Window Sounds for Sleeping | Deep Sleep",
            "⛈️ Thunderstorm Sounds for Sleeping | Heavy Rain",
            "🌧️ Rain Sounds Black Screen | Deep Sleep White Noise",
            "🌧️ Heavy Rain for Sleep | Rain ASMR No Ads",
            "⛈️ Rain and Thunder Sounds | Sleep Instantly Tonight",
            "🌧️ Relaxing Rain Sounds for Sleeping | White Noise",
            "⛈️ Heavy Rain at Night | Deep Sleep Sounds No Ads",
            "🌧️ Rain Sounds for Studying | Heavy Rain Ambience",
            "⛈️ Thunderstorm Heavy Rain | Insomnia Relief Sleep",
            "🌧️ Gentle Rain Sounds for Deep Sleep | No Ads",
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
        """
        High quality SEO optimized description
        Using high search volume keywords
        """
        return (
            f"{title}\n"
            f"{part_info}\n"
            f"Fall asleep fast with our heavy rain "
            f"sounds for sleeping. These powerful "
            f"rain sounds for sleep create the "
            f"perfect white noise environment to "
            f"help you beat insomnia and achieve "
            f"deep sleep tonight.\n\n"
            f"Our relaxing rain sounds have helped "
            f"thousands of people with insomnia "
            f"symptoms finally get the rest they "
            f"deserve. The gentle rain and thunder "
            f"sounds block out distracting noise "
            f"and calm your mind naturally.\n\n"
            f"PERFECT FOR:\n"
            f"Rain sounds for sleeping all night\n"
            f"Deep sleep and insomnia relief\n"
            f"White noise for sleeping\n"
            f"Rain sounds for studying and focus\n"
            f"Stress relief and anxiety relief\n"
            f"Meditation and relaxation music\n"
            f"Tinnitus relief with rain noise\n"
            f"Sleep music with no ads\n"
            f"Thunder and rain sounds for sleep\n"
            f"Rain ASMR and soothing rain\n\n"
            f"WHY RAIN SOUNDS HELP SLEEP:\n"
            f"Heavy rain creates natural white "
            f"noise that masks disruptive sounds. "
            f"The steady sound of rain triggers "
            f"your relaxation response, reducing "
            f"cortisol levels and preparing your "
            f"body for deep restorative sleep. "
            f"Many people with sleep disorders "
            f"find that rain sounds help them "
            f"sleep instantly.\n\n"
            f"Subscribe for daily rain sounds\n"
            f"Like if this helped you sleep\n"
            f"Comment your favorite rain sound\n\n"
            f"{self._hashtags()}"
        )
