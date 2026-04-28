"""
AI Generator
Generates titles and descriptions using OpenRouter
"""

import os
import random
import requests


class AIGenerator:

    def __init__(self):
        self.api_key = os.getenv(
            "OPENROUTER_API_KEY", ""
        )
        self.model = "mistralai/mistral-7b-instruct"

    def generate_metadata(self, audio_name, part_num=None, total_parts=None):
        """Generate title and description"""

        print("   🤖 Generating AI metadata...")

        title = self._generate_title(
            audio_name, part_num, total_parts
        )
        desc  = self._generate_description(
            title, part_num, total_parts
        )

        return title, desc

    def _generate_title(
        self, audio_name,
        part_num=None, total_parts=None
    ):
        """Generate YouTube title"""

        if not self.api_key:
            return self._fallback_title(
                part_num, total_parts
            )

        try:
            prompt = (
                f"Generate a YouTube title for a "
                f"heavy rain deep sleep video. "
                f"Audio: {audio_name}. "
                f"Make it SEO friendly, "
                f"relaxing and sleep-focused. "
                f"Include emojis. "
                f"Max 80 characters. "
                f"Only return the title, nothing else."
            )

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type" : "application/json",
                },
                json={
                    "model"   : self.model,
                    "messages": [{
                        "role"   : "user",
                        "content": prompt
                    }],
                    "max_tokens": 100,
                },
                timeout=30
            )

            if response.status_code == 200:
                title = response.json()[
                    "choices"
                ][0]["message"]["content"].strip()
                title = title.strip('"\'')

                if part_num and total_parts and total_parts > 1:
                    title = (
                        f"{title} "
                        f"| Part {part_num}/{total_parts}"
                    )
                return title

        except Exception as e:
            print(f"   ⚠️ AI title error: {e}")

        return self._fallback_title(
            part_num, total_parts
        )

    def _generate_description(
        self, title,
        part_num=None, total_parts=None
    ):
        """Generate YouTube description"""

        base_desc = (
            f"🌧️ {title}\n\n"
            f"Fall asleep to the soothing sound of "
            f"heavy rain. Perfect for deep sleep, "
            f"relaxation, meditation, and stress relief.\n\n"
        )

        if part_num and total_parts and total_parts > 1:
            base_desc += (
                f"📌 Part {part_num} of {total_parts}\n\n"
            )

        base_desc += (
            f"🎵 Perfect for:\n"
            f"✅ Deep Sleep\n"
            f"✅ Insomnia Relief\n"
            f"✅ Relaxation\n"
            f"✅ Study & Focus\n"
            f"✅ Meditation\n"
            f"✅ Stress Relief\n"
            f"✅ Anxiety Relief\n\n"
            f"🔔 Subscribe for daily rain sounds!\n"
            f"👍 Like if this helped you sleep!\n\n"
            f"#rainsounds #deepsleep #sleepmusic "
            f"#heavyrain #relax #meditation "
            f"#insomnia #stressrelief #whitenoise "
            f"#rainasmr #sleepaid #calmmusic"
        )

        return base_desc

    def _fallback_title(
        self, part_num=None, total_parts=None
    ):
        """Fallback titles if AI fails"""
        titles = [
            "🌧️ Heavy Rain Sounds for Deep Sleep",
            "⛈️ Thunderstorm Rain for Sleep & Relaxation",
            "🌨️ Heavy Rain on Window for Deep Sleep",
            "🌧️ Rain Sounds to Fall Asleep Fast",
            "⛈️ Heavy Rainfall for Insomnia Relief",
            "🌧️ Deep Sleep Rain Sounds - No Ads",
            "🌨️ Relaxing Heavy Rain for Deep Sleep",
            "⛈️ Rain & Thunder Sounds for Sleep",
        ]

        title = random.choice(titles)

        if part_num and total_parts and total_parts > 1:
            title = (
                f"{title} "
                f"| Part {part_num}/{total_parts}"
            )

        return title