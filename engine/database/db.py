import json
import sqlite3
from contextlib import contextmanager

from engine.config import Config
from engine.utils.logger import get_logger
from engine.database.models import Post, Trend, Content, PipelineRun

logger = get_logger("DatabaseManager")


class DatabaseManager:

    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.create_tables()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def create_tables(self):
        with self._conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS pipeline_runs (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    status      TEXT    DEFAULT 'running',
                    posts_count INTEGER DEFAULT 0,
                    trends_count INTEGER DEFAULT 0,
                    duration_sec REAL   DEFAULT 0.0,
                    error       TEXT    DEFAULT '',
                    created_at  TEXT    NOT NULL
                );

                CREATE TABLE IF NOT EXISTS posts (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    title         TEXT    NOT NULL,
                    source        TEXT    NOT NULL,
                    url           TEXT    DEFAULT '',
                    score         INTEGER DEFAULT 0,
                    cluster       INTEGER DEFAULT -1,
                    trend_score   REAL    DEFAULT 0.0,
                    trend_state   TEXT    DEFAULT 'unknown',
                    cluster_state TEXT    DEFAULT 'unknown',
                    run_id        TEXT    DEFAULT '',
                    created_at    TEXT    NOT NULL
                );

                CREATE TABLE IF NOT EXISTS trends (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    cluster_id    INTEGER NOT NULL,
                    cluster_state TEXT    NOT NULL,
                    cluster_score REAL    DEFAULT 0.0,
                    top_topics    TEXT    DEFAULT '[]',
                    keywords      TEXT    DEFAULT '[]',
                    post_count    INTEGER DEFAULT 0,
                    forecast      TEXT    DEFAULT 'stable',
                    run_id        TEXT    DEFAULT '',
                    created_at    TEXT    NOT NULL
                );

                CREATE TABLE IF NOT EXISTS content (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy   TEXT DEFAULT '',
                    instagram  TEXT DEFAULT '',
                    linkedin   TEXT DEFAULT '',
                    twitter    TEXT DEFAULT '',
                    video      TEXT DEFAULT '',
                    run_id     TEXT DEFAULT '',
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_posts_run    ON posts(run_id);
                CREATE INDEX IF NOT EXISTS idx_posts_state  ON posts(trend_state);
                CREATE INDEX IF NOT EXISTS idx_trends_run   ON trends(run_id);
                CREATE INDEX IF NOT EXISTS idx_trends_state ON trends(cluster_state);
            """)
        logger.info(f"Database ready: {self.db_path}")

    def start_run(self) -> str:
        from datetime import datetime
        run = PipelineRun(created_at=datetime.utcnow().isoformat())
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO pipeline_runs (status, created_at) VALUES (?, ?)",
                (run.status, run.created_at)
            )
            run_id = str(cur.lastrowid)
        logger.info(f"Pipeline run started: {run_id}")
        return run_id

    def finish_run(self, run_id: str, posts_count: int,
                   trends_count: int, duration_sec: float, error: str = ""):
        status = "failed" if error else "completed"
        with self._conn() as conn:
            conn.execute("""
                UPDATE pipeline_runs
                SET status=?, posts_count=?, trends_count=?,
                    duration_sec=?, error=?
                WHERE id=?
            """, (status, posts_count, trends_count, duration_sec, error, run_id))
        logger.info(f"Pipeline run {run_id} {status} in {duration_sec:.1f}s")

    def get_runs(self, limit: int = 20) -> list:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM pipeline_runs ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]

    def save_posts(self, posts: list, run_id: str) -> int:
        if not posts:
            return 0
        from datetime import datetime
        now = datetime.utcnow().isoformat()
        rows = [
            (
                p.get("title", ""),
                p.get("source", ""),
                p.get("url", ""),
                p.get("score", 0),
                p.get("cluster", -1),
                p.get("trend_score", 0.0),
                p.get("trend_state", "unknown"),
                p.get("cluster_state", "unknown"),
                run_id,
                p.get("created_at", now),
            )
            for p in posts
            if p.get("title", "").strip()
        ]
        with self._conn() as conn:
            conn.executemany("""
                INSERT INTO posts
                    (title, source, url, score, cluster, trend_score,
                     trend_state, cluster_state, run_id, created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, rows)
        logger.info(f"Saved {len(rows)} posts (run: {run_id})")
        return len(rows)

    def get_posts(self, run_id: str = None,
                  trend_state: str = None, limit: int = 100) -> list:
        query = "SELECT * FROM posts WHERE 1=1"
        params = []
        if run_id:
            query += " AND run_id=?"
            params.append(run_id)
        if trend_state:
            query += " AND trend_state=?"
            params.append(trend_state)
        query += " ORDER BY trend_score DESC LIMIT ?"
        params.append(limit)
        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def save_trends(self, ranked: dict, run_id: str) -> int:
        saved = 0
        from datetime import datetime
        now = datetime.utcnow().isoformat()
        with self._conn() as conn:
            for bucket, posts in ranked.items():
                for post in posts:
                    conn.execute("""
                        INSERT INTO trends
                            (cluster_id, cluster_state, cluster_score,
                             top_topics, keywords, post_count,
                             forecast, run_id, created_at)
                        VALUES (?,?,?,?,?,?,?,?,?)
                    """, (
                        post.get("cluster", -1),
                        post.get("trend_state", bucket),
                        post.get("cluster_score", post.get("trend_score", 0)),
                        json.dumps([post.get("title", "")], ensure_ascii=False),
                        json.dumps(post.get("keywords", []), ensure_ascii=False),
                        1,
                        post.get("forecast", "stable"),
                        run_id,
                        now,
                    ))
                    saved += 1
        logger.info(f"Saved {saved} trends (run: {run_id})")
        return saved

    def get_trends(self, cluster_state: str = None,
                   run_id: str = None, limit: int = 50) -> list:
        query = "SELECT * FROM trends WHERE 1=1"
        params = []
        if cluster_state:
            query += " AND cluster_state=?"
            params.append(cluster_state)
        if run_id:
            query += " AND run_id=?"
            params.append(run_id)
        query += " ORDER BY cluster_score DESC LIMIT ?"
        params.append(limit)
        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
        results = []
        for r in rows:
            row = dict(r)
            row["top_topics"] = json.loads(row.get("top_topics", "[]"))
            row["keywords"]   = json.loads(row.get("keywords",   "[]"))
            results.append(row)
        return results

    def get_latest_trends(self, state: str = None) -> list:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT id FROM pipeline_runs WHERE status='completed' ORDER BY id DESC LIMIT 1"
            ).fetchone()
        if not row:
            return []
        return self.get_trends(cluster_state=state, run_id=str(row["id"]))

    def save_content(self, strategy: str, content: str, run_id: str) -> int:
        from datetime import datetime
        # Bug Fix: أي header يحتوي على الكلمة (مش exact match)
        instagram = _extract_section(content, r"INSTAGRAM")
        linkedin  = _extract_section(content, r"LINKEDIN")
        twitter   = _extract_section(content, r"TWITTER")
        video     = _extract_section(content, r"VIDEO")   # يمسك SHORT VIDEO SCRIPT كمان
        with self._conn() as conn:
            cur = conn.execute("""
                INSERT INTO content
                    (strategy, instagram, linkedin, twitter, video, run_id, created_at)
                VALUES (?,?,?,?,?,?,?)
            """, (strategy, instagram, linkedin, twitter, video,
                  run_id, datetime.utcnow().isoformat()))
            return cur.lastrowid

    def get_latest_content(self) -> dict:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM content ORDER BY id DESC LIMIT 1"
            ).fetchone()
        return dict(row) if row else None

    def get_stats(self) -> dict:
        with self._conn() as conn:
            total_posts  = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
            total_trends = conn.execute("SELECT COUNT(*) FROM trends").fetchone()[0]
            total_runs   = conn.execute("SELECT COUNT(*) FROM pipeline_runs").fetchone()[0]
            exploding    = conn.execute(
                "SELECT COUNT(*) FROM trends WHERE cluster_state='exploding'"
            ).fetchone()[0]
            growing      = conn.execute(
                "SELECT COUNT(*) FROM trends WHERE cluster_state='growing'"
            ).fetchone()[0]
        return {
            "total_posts":  total_posts,
            "total_trends": total_trends,
            "total_runs":   total_runs,
            "exploding":    exploding,
            "growing":      growing,
        }

    # --- دالة مضافة حديثاً للـ Dashboard ---
    def get_dashboard_data(self) -> dict:
        """جلب ملخص كامل لكل البيانات لتغذية شاشة Dashboard"""
        with self._conn() as conn:
            # 1. الإحصائيات الأساسية
            stats = self.get_stats()
            
            # 2. توزيع المصادر (Source Distribution) للرسم البياني
            source_rows = conn.execute("""
                SELECT source, COUNT(*) as count 
                FROM posts 
                GROUP BY source
            """).fetchall()
            sources = {row['source']: row['count'] for row in source_rows}
            
            # 3. توزيع حالات الترندات
            trend_rows = conn.execute("""
                SELECT cluster_state, COUNT(*) as count 
                FROM trends 
                GROUP BY cluster_state
            """).fetchall()
            trends_dist = {row['cluster_state']: row['count'] for row in trend_rows}
            
            return {
                "stats": stats,
                "sources": sources,
                "trends_dist": trends_dist
            }


def _extract_section(text: str, section: str) -> str:
    """
    Bug Fix: pattern أشمل يمسك أي header يحتوي على الكلمة.
    مثال: VIDEO يمسك 'SHORT VIDEO SCRIPT' و 'VIDEO SCRIPT' و 'VIDEO POST'
    """
    import re
    pattern = rf"##\s*[A-Z\s]*{section}[A-Z\s]*\n(.*?)(?=\n##|\Z)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


_db_instance = None

def get_db() -> DatabaseManager:
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance