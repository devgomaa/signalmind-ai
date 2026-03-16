from engine.utils.logger import get_logger
from engine.ai.gemini_client import GeminiClient

logger = get_logger("ContentGenerationAgent")


class ContentGenerationAgent:
    """
    يحوّل الاستراتيجية إلى محتوى جاهز للنشر على 4 منصات.

    Bug Fix #4: FullPipeline يستدعي content_agent.generate(strategies)
    لكن الكود القديم عنده generate_posts() فقط.
    الحل: إضافة generate() كـ alias.
    """

    def __init__(self):
        self.llm = GeminiClient()

    def generate_posts(self, strategy):
        """يولد محتوى جاهز للنشر على 4 منصات."""
        logger.info("Generating content posts")

        if not strategy:
            logger.warning("Empty strategy received")
            return ""

        prompt = f"""
You are a professional social media content creator.

Using this content strategy:
---
{strategy}
---

Generate ready-to-publish content for each platform:

## INSTAGRAM POST
(150-200 words, engaging caption, 10 relevant hashtags)

## LINKEDIN POST
(200-300 words, professional tone, insight-driven, no hashtags spam)

## TWITTER THREAD
(8-10 tweets, numbered 1/ 2/ 3/ ..., punchy and viral)

## SHORT VIDEO SCRIPT
(60 seconds max, hook in first 3 seconds, clear CTA at end)

---
Write each section completely. Be specific, not generic.
"""

        response = self.llm.ask(prompt)
        logger.info("Content posts generated")
        return response

    # Bug Fix #4: FullPipeline يستدعي .generate() — alias
    def generate(self, strategies):
        return self.generate_posts(strategies)