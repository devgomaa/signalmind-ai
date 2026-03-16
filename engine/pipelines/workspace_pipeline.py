"""
engine/pipelines/workspace_pipeline.py
========================================
Sprint 6: Pipeline مخصص لكل workspace بـ niche و market.
"""

import time
from engine.utils.logger import get_logger
from engine.utils.data_writer import save_json
from engine.config import Config
from engine.database import get_db
from engine.auth.auth_manager import get_auth
from engine.workspace.niche_config import NICHE_CONFIG, get_niche_prompt, get_deep_search_prompt

logger = get_logger("WorkspacePipeline")


class WorkspacePipeline:
    """
    نفس FullPipeline لكن:
    - يجيب إعدادات الـ workspace (niche + markets)
    - يفلتر الـ scrapers بناءً على الـ niche
    - يخصّص الـ Gemini prompts
    - يحفظ النتائج مع workspace_id
    """

    def __init__(self, workspace_id: int):
        self.workspace_id = workspace_id
        ws = get_auth().get_workspace(workspace_id)
        if not ws:
            raise ValueError(f"Workspace {workspace_id} not found")

        self.niche   = ws.get("niche", "tech")
        self.markets = ws.get("markets", ["global"])
        self.ws_name = ws.get("name", f"WS {workspace_id}")

        self._niche_cfg = NICHE_CONFIG.get(self.niche, NICHE_CONFIG["tech"])

    def run(self):
        start_time = time.time()
        db     = get_db()
        run_id = db.start_run()

        logger.info(f"WorkspacePipeline started — ws:{self.workspace_id} "
                    f"niche:{self.niche} markets:{self.markets}")

        try:
            # 1. Scraping
            from engine.agents.scraping_agent import ScrapingAgent
            posts = ScrapingAgent().collect_posts()
            posts = self._filter_by_niche(posts)
            logger.info(f"After niche filter: {len(posts)} posts")

            # Tag with workspace_id
            for p in posts:
                p["workspace_id"] = self.workspace_id

            save_json(Config.DATA_RAW_PATH, posts)
            self._save_posts_ws(posts, run_id, db)

            # 2. Deep Search (niche-specific prompt)
            from engine.ai.gemini_client import GeminiClient
            llm = GeminiClient()
            try:
                deep_prompt = get_deep_search_prompt(self.niche, self.markets)
                response    = llm.ask(deep_prompt)
                deep_posts  = self._parse_deep_response(response)
                for p in deep_posts:
                    p["workspace_id"] = self.workspace_id
                posts.extend(deep_posts)
                logger.info(f"Deep search added {len(deep_posts)} topics")
            except Exception as e:
                logger.warning(f"Deep search skipped: {e}")

            # 3. Trend Intelligence
            from engine.agents.trend_intelligence_agent import TrendIntelligenceAgent
            trends = TrendIntelligenceAgent().detect_trends(posts)
            save_json(Config.DATA_TRENDS_PATH, trends)
            self._save_trends_ws(trends, run_id, db)

            # 4. Content Strategy (niche-specific)
            flat_trends = []
            for bucket in ["exploding", "growing", "future", "stable"]:
                flat_trends.extend(trends.get(bucket, []))
            topics = [t.get("title", "") for t in flat_trends[:10] if t.get("title")]

            strategy = ""
            content  = ""
            try:
                strategy_prompt = get_niche_prompt(self.niche, self.markets, topics)
                strategy        = llm.ask(strategy_prompt)

                content_prompt = f"""
Using this {self._niche_cfg['label']} content strategy:
{strategy}

Generate ready-to-publish content:
## INSTAGRAM POST
## LINKEDIN POST
## TWITTER THREAD
## SHORT VIDEO SCRIPT
"""
                content = llm.ask(content_prompt)
            except Exception as e:
                logger.warning(f"Content generation skipped: {e}")

            save_json(Config.DATA_CONTENT_PATH, {"strategy": strategy, "content": content})
            if strategy:
                db.save_content(strategy, content, run_id)

            duration    = time.time() - start_time
            trend_count = sum(len(v) for v in trends.values())
            db.finish_run(run_id, len(posts), trend_count, duration)

            logger.info(f"WorkspacePipeline done in {duration:.1f}s — "
                        f"{len(posts)} posts, {trend_count} trends")

            return {"run_id": run_id, "posts": len(posts),
                    "trends": trend_count, "duration": duration}

        except Exception as e:
            duration = time.time() - start_time
            db.finish_run(run_id, 0, 0, duration, error=str(e))
            logger.error(f"WorkspacePipeline failed: {e}")
            raise

    def _filter_by_niche(self, posts: list) -> list:
        """فلترة البوستات بناءً على keywords الـ niche."""
        keywords = [k.lower() for k in self._niche_cfg.get("keywords", [])]
        if not keywords:
            return posts

        filtered = []
        for post in posts:
            title = post.get("title", "").lower()
            # لو العنوان يحتوي على أي keyword من الـ niche — اتضيف
            if any(kw in title for kw in keywords):
                filtered.append(post)

        # لو الفلترة شالت أكتر من 70% من البوستات — نرجع كل البوستات
        # (يحصل مع niches واسعة زي marketing)
        if len(filtered) < len(posts) * 0.3:
            logger.warning("Niche filter too aggressive — using all posts")
            return posts

        return filtered

    def _parse_deep_response(self, response: str) -> list:
        posts = []
        for line in response.split("\n"):
            line = line.strip()
            if not line or len(line) < 5:
                continue
            if line[0].isdigit():
                parts = line.split(".", 1) if "." in line[:3] else line.split(")", 1)
                if len(parts) == 2:
                    line = parts[1].strip()
            elif line.startswith("-"):
                line = line[1:].strip()
            if len(line) >= 5:
                posts.append({
                    "title": line, "url": "", "source": "deep_search",
                    "score": 1, "workspace_id": self.workspace_id
                })
        return posts

    def _save_posts_ws(self, posts: list, run_id: str, db):
        """حفظ posts مع workspace_id."""
        db.save_posts(posts, run_id)

    def _save_trends_ws(self, trends: dict, run_id: str, db):
        """حفظ trends مع workspace_id."""
        db.save_trends(trends, run_id)
