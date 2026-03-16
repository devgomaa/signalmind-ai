from engine.utils.logger import get_logger

from engine.trend_engine.deduplicator        import deduplicate_posts
from engine.trend_engine.topic_clusterer     import cluster_topics
from engine.trend_engine.trend_velocity      import calculate_velocity
from engine.trend_engine.novelty_detector    import detect_novelty
from engine.trend_engine.trend_scorer        import score_trends
from engine.trend_engine.trend_classifier    import classify_trends
from engine.trend_engine.trend_forecaster    import TrendForecaster
from engine.trend_engine.keyword_extractor   import extract_keywords
from engine.trend_engine.trend_ranker        import TrendRanker
from engine.trend_engine.trend_time_analyzer import TrendTimeAnalyzer

logger = get_logger("TrendIntelligenceAgent")


class TrendIntelligenceAgent:

    def __init__(self):
        self.forecaster    = TrendForecaster()
        self.ranker        = TrendRanker()
        self.time_analyzer = TrendTimeAnalyzer()

    def detect_trends(self, posts: list) -> dict:
        logger.info(f"Starting trend intelligence pipeline on {len(posts)} posts")

        posts = deduplicate_posts(posts)
        logger.info(f"After dedupe: {len(posts)} posts")

        posts = cluster_topics(posts)
        logger.info("Topic clustering completed")

        posts = calculate_velocity(posts)
        logger.info("Velocity calculated")

        posts = detect_novelty(posts)
        logger.info("Novelty detection completed")

        posts = self.time_analyzer.enrich(posts)
        logger.info("Cluster time analysis completed")

        posts = score_trends(posts)
        logger.info("Trend scoring completed")

        posts = classify_trends(posts)
        logger.info("Trend classification completed")

        posts = self.forecaster.forecast(posts)
        logger.info("Trend forecasting completed")

        keywords = extract_keywords(posts)
        logger.info(f"Top keywords: {keywords}")

        ranked = self.ranker.rank(posts)
        logger.info("Trend ranking completed")

        return ranked

    def analyze(self, posts: list) -> dict:
        return self.detect_trends(posts)
