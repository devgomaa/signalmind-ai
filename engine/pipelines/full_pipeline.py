"""
engine/pipelines/full_pipeline.py
==================================
Sprint 3: ربط الـ database مع الـ pipeline.

التغييرات:
    - كل run بيتسجل في pipeline_runs table
    - البوستات بتتحفظ في posts table
    - الترندات بتتحفظ في trends table
    - المحتوى بيتحفظ في content table
    - لسه بيحفظ JSON برضو (backward compat)
"""

import time

from engine.utils.logger import get_logger
from engine.utils.data_writer import save_json
from engine.config import Config
from engine.database import get_db

from engine.agents.scraping_agent         import ScrapingAgent
from engine.agents.deep_search_agent      import DeepSearchAgent
from engine.agents.trend_intelligence_agent import TrendIntelligenceAgent
from engine.agents.content_strategy_agent  import ContentStrategyAgent
from engine.agents.content_generation_agent import ContentGenerationAgent

logger = get_logger("FullPipeline")


class FullPipeline:

    def __init__(self):
        self.scraper        = ScrapingAgent()
        self.deep_search    = DeepSearchAgent()
        self.trend_agent    = TrendIntelligenceAgent()
        self.strategy_agent = ContentStrategyAgent()
        self.content_agent  = ContentGenerationAgent()
        self.db             = get_db()

    def run(self):
        start_time = time.time()
        run_id = self.db.start_run()

        logger.info("=" * 50)
        logger.info(f"PIPELINE STARTED  (run_id: {run_id})")
        logger.info("=" * 50)

        try:
            # 1. Scraping
            posts = self.scraper.collect_posts()
            logger.info(f"Collected {len(posts)} posts from scrapers")

            # 2. Deep Search
            posts = self.deep_search.expand_topics(posts)
            logger.info(f"After deep search: {len(posts)} posts")

            # حفظ البوستات الخام (JSON + DB)
            save_json(Config.DATA_RAW_PATH, posts)
            self.db.save_posts(posts, run_id)

            # 3. Trend Intelligence
            trends = self.trend_agent.detect_trends(posts)
            logger.info(
                f"Trends — exploding: {len(trends.get('exploding', []))}, "
                f"growing: {len(trends.get('growing', []))}, "
                f"future: {len(trends.get('future', []))}"
            )

            # حفظ الترندات (JSON + DB)
            save_json(Config.DATA_TRENDS_PATH, trends)
            self.db.save_trends(trends, run_id)

            # 4. Content Strategy
            strategies = self.strategy_agent.generate(trends)
            logger.info("Content strategy generated")

            # 5. Content Generation
            content = self.content_agent.generate(strategies)
            logger.info("Content generation completed")

            # حفظ المحتوى (JSON + DB)
            save_json(Config.DATA_CONTENT_PATH, {
                "strategy": strategies,
                "content":  content,
            })
            self.db.save_content(strategies, content, run_id)

            # تسجيل نهاية الـ run
            duration = time.time() - start_time
            total_trends = sum(len(v) for v in trends.values())
            self.db.finish_run(run_id, len(posts), total_trends, duration)

            logger.info("=" * 50)
            logger.info(f"PIPELINE COMPLETED in {duration:.1f}s")
            logger.info("=" * 50)

            return {
                "run_id":     run_id,
                "posts":      posts,
                "trends":     trends,
                "strategies": strategies,
                "content":    content,
            }

        except Exception as e:
            duration = time.time() - start_time
            self.db.finish_run(run_id, 0, 0, duration, error=str(e))
            logger.error(f"Pipeline failed: {e}")
            raise