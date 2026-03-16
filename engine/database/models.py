"""
engine/database/models.py
=========================
Sprint 3: تعريف الـ database models.
⚠️ ملف جديد — مش موجود في المشروع الأصلي.

نستخدم dataclasses بدل ORM عشان:
    - مفيش dependencies إضافية (SQLAlchemy وزنها تقيل)
    - SQLite built-in في Python
    - سهل الفهم والتعديل

الـ 3 tables:
    Post    — البوستات الخام من الـ scrapers
    Trend   — الترندات المحللة
    Content — المحتوى المولّد
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Post:
    """
    بوست خام من أي scraper.
    يتحفظ بعد الـ scraping وقبل الـ trend analysis.
    """
    title:      str
    source:     str
    url:        str         = ""
    score:      int         = 0
    cluster:    int         = -1          # -1 = لسه متكلسترش
    trend_score:    float   = 0.0
    trend_state:    str     = "unknown"
    cluster_state:  str     = "unknown"
    run_id:     str         = ""          # لربط كل البوستات بـ pipeline run واحد
    created_at: str         = field(default_factory=lambda: datetime.utcnow().isoformat())
    id:         Optional[int] = None      # بيتملى من الـ DB


@dataclass
class Trend:
    """
    ترند محلل — cluster كامل مع summary.
    يتحفظ بعد الـ TrendRanker.
    """
    cluster_id:     int
    cluster_state:  str           # exploding / growing / future / stable
    cluster_score:  float
    top_topics:     str           # JSON string للـ top 5 عناوين
    keywords:       str           # JSON string
    post_count:     int
    forecast:       str           = "stable"
    run_id:         str           = ""
    created_at:     str           = field(default_factory=lambda: datetime.utcnow().isoformat())
    id:             Optional[int] = None


@dataclass
class Content:
    """
    محتوى مولّد جاهز للنشر.
    يتحفظ بعد الـ ContentGenerationAgent.
    """
    strategy:   str           # الاستراتيجية كاملة
    instagram:  str   = ""
    linkedin:   str   = ""
    twitter:    str   = ""
    video:      str   = ""
    run_id:     str   = ""
    created_at: str   = field(default_factory=lambda: datetime.utcnow().isoformat())
    id:         Optional[int] = None


@dataclass
class PipelineRun:
    """
    سجل لكل تشغيل للـ pipeline.
    يسمح بمقارنة الترندات عبر الزمن.
    """
    status:         str   = "running"     # running / completed / failed
    posts_count:    int   = 0
    trends_count:   int   = 0
    duration_sec:   float = 0.0
    error:          str   = ""
    created_at:     str   = field(default_factory=lambda: datetime.utcnow().isoformat())
    id:             Optional[int] = None