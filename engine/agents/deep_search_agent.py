from engine.utils.logger import get_logger
from engine.ai.gemini_client import GeminiClient

logger = get_logger("DeepSearchAgent")


class DeepSearchAgent:
    """
    يستخدم Gemini لاكتشاف ترندات مخفية غير موجودة في الـ scrapers.

    Bug Fix #3: FullPipeline يستدعي expand_topics(posts) — الـ method
    لم تكن موجودة. الكود القديم كان عنده discover_trends() فقط.

    الحل:
        - discover_trends()  : يرجع ترندات جديدة من Gemini
        - expand_topics(posts): يدمج الترندات الجديدة مع posts الموجودة
          (هذه هي الـ method التي يستدعيها FullPipeline)
    """

    def __init__(self):
        self.llm = GeminiClient()

    def discover_trends(self):
        """يسأل Gemini عن 20 ترند ناشئ ويرجعها كـ list of dicts."""
        logger.info("Running deep search via Gemini")

        prompt = """
You are a tech trend analyst.

Find 20 emerging technology and startup trends right now across:
Reddit, Twitter, LinkedIn, Product Hunt, GitHub, Hacker News.

Return ONLY a numbered list, one trend per line, like this:
1. AI coding agents replacing junior developers
2. Vector databases becoming mainstream
3. ...

No extra text, no descriptions, just the numbered list.
"""

        response = self.llm.ask(prompt)
        trends = []

        for line in response.split("\n"):
            line = line.strip()

            if not line or len(line) < 5:
                continue

            # إزالة الترقيم في البداية (1. أو 1) أو -)
            if line[0].isdigit():
                # إزالة "1." أو "1)"
                parts = line.split(".", 1) if "." in line[:3] else line.split(")", 1)
                if len(parts) == 2:
                    line = parts[1].strip()

            elif line.startswith("-"):
                line = line[1:].strip()

            if len(line) < 5:
                continue

            trends.append({
                "title": line,
                "url": "",
                "source": "deep_search",
                "score": 1
            })

        logger.info(f"Deep search discovered {len(trends)} topics")
        return trends

    def expand_topics(self, posts):
        """
        Bug Fix #3: هذه الـ method التي يستدعيها FullPipeline.
        تضيف الترندات المكتشفة من Gemini على posts الموجودة.
        """
        new_trends = self.discover_trends()
        posts.extend(new_trends)
        logger.info(f"Posts after deep search expansion: {len(posts)}")
        return posts