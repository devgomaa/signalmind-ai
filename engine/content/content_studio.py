"""
engine/content/content_studio.py
==================================
Content Studio Orchestrator

Flow:
1. Gemini → generate ideas JSON
2. MediaService → generate images or videos
3. Return structured response for API
"""

import os
import json
import re
from dataclasses import dataclass
from typing import Optional

from engine.utils.logger import get_logger
from engine.ai.gemini_client import GeminiClient
from engine.content.media_service import MediaService

logger = get_logger("ContentStudio")

OUTPUT_DIR = "output_content"


# ══════════════════════════════════════════════
# DATA CLASSES
# ══════════════════════════════════════════════

@dataclass
class GeneratedPost:
    idea_index: int
    hook: str
    post_copy: str
    hashtags: list
    image_path: Optional[str] = None
    status: str = "pending"
    error: Optional[str] = None


@dataclass
class GeneratedVideo:
    idea_index: int
    hook: str
    script: list
    video_path: Optional[str] = None
    status: str = "pending"
    error: Optional[str] = None


# ══════════════════════════════════════════════
# CONTENT STUDIO — Main Orchestrator
# ══════════════════════════════════════════════

class ContentStudio:
    """
    Main orchestrator.

    Steps:
    1. Gemini → generate ideas JSON
    2. MediaService → generate images or videos
    """

    def __init__(self, workspace_id: int = 1):
        self.workspace_id = workspace_id
        self.llm = GeminiClient()
        self.media = MediaService()

        os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ══════════════════════════════════════════════
    # MAIN ENTRY
    # ══════════════════════════════════════════════

    def generate_content(
        self,
        topic: str,
        content_type: str,
        niche: str = "tech",
        language: str = "English",
        brand_colors: list = None,
        num_ideas: int = 3,
        platforms: list = None,
        comp_insight: str = None,
        trend_insight: str = None,
    ) -> dict:

        brand_colors = brand_colors or ["#3B82F6"]
        platforms = platforms or ["Instagram", "LinkedIn"]

        logger.info(
            f"ContentStudio generating {content_type} for '{topic}' (niche:{niche})"
        )

        # ── Step 1: Generate ideas JSON ──
        ideas_json = self._generate_ideas(
            topic,
            content_type,
            niche,
            language,
            brand_colors,
            num_ideas,
            platforms,
            comp_insight,
            trend_insight,
        )

        if not ideas_json or "ideas" not in ideas_json:
            return {"status": "failed", "error": "No ideas generated"}
        ideas = ideas_json["ideas"]

        # ── Step 2: Generate media via MediaService ──
        results = []

        if content_type == "static":

            media_results = self.media.generate_static_posts(
                {"ideas": ideas}
            )

            for i, r in enumerate(media_results):

                idea = ideas[i]

                results.append({
                    "idea_index": i + 1,
                    "type": "static",
                    "hook": idea.get("hook"),
                    "post_copy": idea.get("post_copy"),
                    "hashtags": idea.get("hashtags"),
                    "image_path": r.image_path,
                    "image_url": f"/api/content/media/{os.path.basename(r.image_path)}"
                    if r.image_path else None,
                    "status": r.status,
                    "error": r.error
                })

        elif content_type == "video":

            media_results = self.media.generate_videos(
                {"ideas": ideas}
            )

            for i, r in enumerate(media_results):

                idea = ideas[i]

                results.append({
                    "idea_index": i + 1,
                    "type": "video",
                    "hook": idea.get("hook"),
                    "script": idea.get("script"),
                    "video_path": r.video_url,
                    "video_url": f"/api/content/media/{os.path.basename(r.video_url)}"
                    if r.video_url else None,
                    "status": r.status,
                    "error": r.error
                })

        return {
            "status": "completed",
            "type": content_type,
            "topic": topic,
            "niche": niche,
            "ideas": results,
            "raw_json": ideas_json,
        }

    # ══════════════════════════════════════════════
    # IDEA GENERATION
    # ══════════════════════════════════════════════

    def _generate_ideas(
    self,
    topic,
    content_type,
    niche,
    language,
    brand_colors,
    num_ideas,
    platforms,
    comp_insight,
    trend_insight,
) -> dict:

        from engine.workspace.niche_config import NICHE_CONFIG
        import json, re, time

        niche_label = NICHE_CONFIG.get(niche, {}).get("label", niche)

        if content_type == "video":
            schema = self._video_schema(num_ideas, language)
        else:
            schema = self._static_schema(num_ideas, language)

        context = f"Topic: {topic}\nNiche: {niche_label}\nPlatforms: {', '.join(platforms)}"

        if comp_insight:
            context += f"\nCompetitor Insights: {comp_insight}"

        if trend_insight:
            context += f"\nCurrent Trends: {trend_insight}"

        prompt = f"""
    You are an expert Social Media Content Creator.

    Topic: {topic}
    Niche: {niche_label}
    Platforms: {', '.join(platforms)}
    Language: {language}

    Brand Colors: {brand_colors}

    {schema}

    Return ONLY valid JSON.
    No markdown.
    No explanation.
    """

        MAX_RETRIES = 3

        for attempt in range(MAX_RETRIES):

            try:
                logger.info(f"LLM attempt {attempt+1}")

                raw = self.llm.ask(prompt, max_tokens=4096)

                logger.info("LLM RAW RESPONSE:")
                logger.info(raw)

                # محاولة استخراج JSON
                match = re.search(r"\{[\s\S]*\}", raw)

                if not match:
                    logger.warning("No JSON detected in LLM response")
                    continue

                parsed = json.loads(match.group())

                if "ideas" not in parsed:
                    logger.warning("JSON missing 'ideas' field")
                    continue

                if not parsed["ideas"]:
                    logger.warning("Ideas list empty")
                    continue

                logger.info(f"{len(parsed['ideas'])} ideas generated")

                return parsed

            except Exception as e:
                logger.error(f"LLM parsing error: {e}")
                time.sleep(1)

        # fallback لو LLM فشل
        logger.warning("Using fallback ideas")

        fallback = {
            "ideas": [
                {
                    "hook": f"Why {topic} is becoming the next big thing",
                    "post_copy": f"Developers and companies are rapidly adopting {topic}. Here's why it matters and how it will shape the future.",
                    "hashtags": ["AI", "Tech", "Innovation", "Future", "Development"],
                    "image_description": f"modern technology concept about {topic}, futuristic digital design",
                    "visual_direction": "modern, clean, futuristic tech aesthetic"
                }
            ]
        }

        return fallback

    # ══════════════════════════════════════════════
    # SCHEMAS
    # ══════════════════════════════════════════════

    def _static_schema(self, num: int, lang: str):

        return f"""
Generate {num} social media posts in {lang}.

Return JSON:

{{
 "ideas":[
  {{
   "hook":"attention grabbing hook",
   "post_copy":"full post text",
   "image_description":"visual description",
   "hashtags":["tag1","tag2","tag3"]
  }}
 ]
}}
"""

    def _video_schema(self, num: int, lang: str):

        return f"""
Generate {num} short video scripts in {lang}.

Return JSON:

{{
 "ideas":[
  {{
   "hook":{{"text":"hook text","duration_seconds":3}},
   "script":[
    {{
     "scene":1,
     "visuals":"scene description",
     "voiceover":"spoken text",
     "duration_seconds":5
    }}
   ],
   "hashtags":["tag1","tag2"]
  }}
 ]
}}
"""