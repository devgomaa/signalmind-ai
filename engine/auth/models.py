"""
engine/auth/models.py
=====================
Sprint 6: User / Workspace / Competitor dataclasses.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

NICHES = [
    "tech",        # Tech / Software
    "marketing",   # Marketing / Content
    "ecommerce",   # E-commerce / Retail
    "finance",     # Finance / Fintech
    "health",      # Health / Medtech
    "education",   # Education / Edtech
    "ai_startup",  # AI / Startups
]

MARKETS = ["egypt", "saudi", "uae", "kuwait", "morocco", "global"]

NICHE_LABELS = {
    "tech":       "Tech / Software",
    "marketing":  "Marketing / Content",
    "ecommerce":  "E-commerce / Retail",
    "finance":    "Finance / Fintech",
    "health":     "Health / Medtech",
    "education":  "Education / Edtech",
    "ai_startup": "AI / Startups",
}

MARKET_LABELS = {
    "egypt":   "🇪🇬 Egypt",
    "saudi":   "🇸🇦 Saudi Arabia",
    "uae":     "🇦🇪 UAE",
    "kuwait":  "🇰🇼 Kuwait",
    "morocco": "🇲🇦 Morocco",
    "global":  "🌍 Global",
}

ROLES = ["admin", "editor", "viewer"]


@dataclass
class User:
    email:         str
    password_hash: str
    name:          str
    workspace_id:  int           = 1
    role:          str           = "admin"   # admin | editor | viewer
    is_active:     bool          = True
    created_at:    str           = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_login:    str           = ""
    id:            Optional[int] = None


@dataclass
class Workspace:
    name:            str
    niche:           str           = "tech"
    markets:         str           = '["global"]'   # JSON list
    schedule_hours:  int           = 6
    owner_id:        int           = 1
    created_at:      str           = field(default_factory=lambda: datetime.utcnow().isoformat())
    id:              Optional[int] = None

    def get_markets(self) -> list:
        try:
            return json.loads(self.markets)
        except Exception:
            return ["global"]

    def set_markets(self, markets: list):
        self.markets = json.dumps(markets)


@dataclass
class Competitor:
    workspace_id:  int
    name:          str
    url:           str           = ""
    competitor_type: str         = "brand"   # brand | influencer | publication
    last_scraped:  str           = ""
    posts_count:   int           = 0
    created_at:    str           = field(default_factory=lambda: datetime.utcnow().isoformat())
    id:            Optional[int] = None
