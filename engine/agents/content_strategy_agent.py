from engine.utils.logger import get_logger
from engine.ai.gemini_client import GeminiClient

logger = get_logger("ContentStrategyAgent")


class ContentStrategyAgent:
    """
    يولد استراتيجية محتوى بناءً على الترندات الأعلى تصنيفاً.

    Bug Fix #4: FullPipeline يستدعي strategy_agent.generate(trends)
    لكن الكود القديم عنده generate_strategy() فقط.
    الحل: إضافة generate() كـ alias.

    Bug Fix #6: الكود القديم كان يعمل trends[:10] مباشرة،
    لكن output الـ TrendRanker هو dict:
        { "exploding": [...], "growing": [...], "future": [...], "stable": [...] }
    وليس list — فكان trends[:10] يرجع أول 10 keys مش posts!

    الحل: flatten_trends() تحوّل الـ dict لـ list مرتبة بالأولوية.
    """

    def __init__(self):
        self.llm = GeminiClient()

    def _flatten_trends(self, trends):
        """
        Bug Fix #6: تحويل ranked dict إلى list مرتبة.
        الأولوية: exploding أولاً ثم growing ثم future ثم stable.
        """
        if isinstance(trends, list):
            # لو بالفعل list (من AIPipeline مثلاً) نرجعها كما هي
            return trends

        if isinstance(trends, dict):
            flat = []
            for bucket in ["exploding", "growing", "future", "stable"]:
                flat.extend(trends.get(bucket, []))
            return flat

        logger.warning(f"Unexpected trends type: {type(trends)}")
        return []

    def generate_strategy(self, trends):
        """يولد استراتيجية محتوى من الترندات."""
        logger.info("Generating content strategy")

        flat_trends = self._flatten_trends(trends)
        top_trends = flat_trends[:10]

        if not top_trends:
            logger.warning("No trends available for strategy generation")
            return ""

        # استخراج العناوين بأمان
        topics = []
        for t in top_trends:
            title = t.get("title", "")
            state = t.get("trend_state", "")
            if title:
                topics.append(f"[{state.upper()}] {title}" if state else title)

        prompt = f"""
You are a viral content strategist for tech and startup audiences.

Based on these trending topics:
{chr(10).join(f"{i+1}. {t}" for i, t in enumerate(topics))}

Generate a complete content strategy with:

1. 10 viral hooks (one per topic or angle)
2. 10 post ideas (platform + angle)
3. 5 thread ideas (Twitter/LinkedIn threads)
4. 5 short video ideas (30-60 seconds)

Format clearly with headers. Be specific and actionable.
"""

        response = self.llm.ask(prompt)
        logger.info("Content strategy generated")
        return response

    # Bug Fix #4: FullPipeline يستدعي .generate() — alias
    def generate(self, trends):
        return self.generate_strategy(trends)