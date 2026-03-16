import asyncio

from engine.utils.logger import get_logger
from engine.utils.data_writer import save_json
from engine.config import Config

from engine.agents.scraping_agent import ScrapingAgent
from engine.agents.deep_search_agent import DeepSearchAgent
from engine.agents.trend_intelligence_agent import TrendIntelligenceAgent
from engine.agents.content_strategy_agent import ContentStrategyAgent
from engine.agents.content_generation_agent import ContentGenerationAgent

logger = get_logger("AIPipeline")


class AIPipeline:
    """
    الـ Pipeline الـ async — نفس FullPipeline لكن مناسب للـ API.

    Bug Fix #2: كان يستدعي trend_agent.analyze() التي لم تكن موجودة.
    تم إضافة analyze() كـ alias لـ detect_trends() في TrendIntelligenceAgent.

    ملاحظة: ScrapingAgent.collect_posts() هو sync (ThreadPoolExecutor).
    run_in_executor يخليه يشتغل بدون block الـ event loop.
    """

    async def run(self):
        logger.info("AIPipeline started (async)")

        loop = asyncio.get_event_loop()

        # 1. Scraping — نشغّله في executor عشان مش async
        scraping_agent = ScrapingAgent()
        posts = await loop.run_in_executor(
            None, scraping_agent.collect_posts
        )
        logger.info(f"Collected {len(posts)} posts")

        # 2. Deep Search
        deep_search = DeepSearchAgent()
        deep_trends = deep_search.discover_trends()
        posts.extend(deep_trends)
        logger.info(f"After deep search: {len(posts)} posts")

        save_json(Config.DATA_RAW_PATH, posts)

        # 3. Trend Intelligence
        # Bug Fix #2: analyze() موجودة الآن كـ alias لـ detect_trends()
        trend_agent = TrendIntelligenceAgent()
        trends = trend_agent.analyze(posts)

        save_json(Config.DATA_TRENDS_PATH, trends)

        # 4. Content Strategy
        strategy_agent = ContentStrategyAgent()
        strategy = strategy_agent.generate_strategy(trends)

        # 5. Content Generation
        content_agent = ContentGenerationAgent()
        content = content_agent.generate_posts(strategy)

        save_json(Config.DATA_CONTENT_PATH, {
            "strategy": strategy,
            "content": content
        })

        logger.info("AIPipeline completed")
        return content