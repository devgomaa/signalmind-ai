"""
engine/auth/auth_manager.py
============================
Sprint 6: JWT authentication + bcrypt password hashing.
"""

import sqlite3
import json
from datetime import datetime, timedelta

import bcrypt
import jwt

from engine.config import Config
from engine.utils.logger import get_logger
from engine.auth.models import User, Workspace, Competitor, NICHES, MARKETS

logger = get_logger("AuthManager")

SECRET_KEY  = Config.SECRET_KEY if hasattr(Config, "SECRET_KEY") else "dev-secret-change-me"
TOKEN_HOURS = 24 * 7   # token valid 7 days


class AuthManager:

    def __init__(self):
        from engine.config import Config
        self.db_path = Config.DATABASE_PATH
        self._create_tables()

    # ── connection ──────────────────────────────────

    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    # ── schema ──────────────────────────────────────

    def _create_tables(self):
        with self._conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS workspaces (
                    id             INTEGER PRIMARY KEY AUTOINCREMENT,
                    name           TEXT    NOT NULL,
                    niche          TEXT    DEFAULT 'tech',
                    markets        TEXT    DEFAULT '["global"]',
                    schedule_hours INTEGER DEFAULT 6,
                    owner_id       INTEGER DEFAULT 1,
                    created_at     TEXT    NOT NULL
                );

                CREATE TABLE IF NOT EXISTS users (
                    id             INTEGER PRIMARY KEY AUTOINCREMENT,
                    email          TEXT    UNIQUE NOT NULL,
                    password_hash  TEXT    NOT NULL,
                    name           TEXT    NOT NULL,
                    workspace_id   INTEGER DEFAULT 1,
                    role           TEXT    DEFAULT 'admin',
                    is_active      INTEGER DEFAULT 1,
                    created_at     TEXT    NOT NULL,
                    last_login     TEXT    DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS competitors (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    workspace_id     INTEGER NOT NULL,
                    name             TEXT    NOT NULL,
                    url              TEXT    DEFAULT '',
                    competitor_type  TEXT    DEFAULT 'brand',
                    last_scraped     TEXT    DEFAULT '',
                    posts_count      INTEGER DEFAULT 0,
                    created_at       TEXT    NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_users_email      ON users(email);
                CREATE INDEX IF NOT EXISTS idx_users_workspace  ON users(workspace_id);
                CREATE INDEX IF NOT EXISTS idx_competitors_ws   ON competitors(workspace_id);
            """)
            conn.commit()
        logger.info("Auth tables ready")

    # ── Workspace CRUD ───────────────────────────────

    def create_workspace(self, name: str, niche: str = "tech",
                         markets: list = None, owner_id: int = 1) -> int:
        if markets is None:
            markets = ["global"]
        now = datetime.utcnow().isoformat()
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO workspaces (name, niche, markets, owner_id, created_at) "
                "VALUES (?,?,?,?,?)",
                (name, niche, json.dumps(markets), owner_id, now)
            )
            conn.commit()
            return cur.lastrowid

    def get_workspace(self, workspace_id: int) -> dict | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM workspaces WHERE id=?", (workspace_id,)
            ).fetchone()
        if not row:
            return None
        d = dict(row)
        try:
            d["markets"] = json.loads(d.get("markets", '["global"]'))
        except Exception:
            d["markets"] = ["global"]
        return d

    def update_workspace(self, workspace_id: int, **kwargs) -> bool:
        allowed = {"name", "niche", "markets", "schedule_hours"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if "markets" in updates and isinstance(updates["markets"], list):
            updates["markets"] = json.dumps(updates["markets"])
        if not updates:
            return False
        set_clause = ", ".join(f"{k}=?" for k in updates)
        values = list(updates.values()) + [workspace_id]
        with self._conn() as conn:
            conn.execute(
                f"UPDATE workspaces SET {set_clause} WHERE id=?", values
            )
            conn.commit()
        return True

    def get_all_workspaces(self) -> list:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM workspaces ORDER BY id").fetchall()
        result = []
        for row in rows:
            d = dict(row)
            try:
                d["markets"] = json.loads(d.get("markets", '["global"]'))
            except Exception:
                d["markets"] = ["global"]
            result.append(d)
        return result

    # ── User CRUD ────────────────────────────────────

    def register(self, email: str, password: str, name: str,
                 workspace_name: str = None, niche: str = "tech",
                 markets: list = None) -> dict:
        """Register new user + create workspace."""
        # check email exists
        with self._conn() as conn:
            existing = conn.execute(
                "SELECT id FROM users WHERE email=?", (email,)
            ).fetchone()
        if existing:
            return {"ok": False, "error": "Email already registered"}

        # hash password
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        now     = datetime.utcnow().isoformat()

        # create workspace first
        ws_name = workspace_name or f"{name}'s Workspace"
        ws_id   = self.create_workspace(ws_name, niche, markets or ["global"])

        # create user
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO users (email, password_hash, name, workspace_id, role, created_at) "
                "VALUES (?,?,?,?,?,?)",
                (email, pw_hash, name, ws_id, "admin", now)
            )
            conn.commit()
            user_id = cur.lastrowid

        # update workspace owner
        with self._conn() as conn:
            conn.execute(
                "UPDATE workspaces SET owner_id=? WHERE id=?", (user_id, ws_id)
            )
            conn.commit()

        token = self._generate_token(user_id, ws_id, "admin")
        logger.info(f"Registered user: {email} (workspace: {ws_id})")
        return {"ok": True, "token": token, "user_id": user_id, "workspace_id": ws_id}

    def login(self, email: str, password: str) -> dict:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE email=? AND is_active=1", (email,)
            ).fetchone()

        if not row:
            return {"ok": False, "error": "Invalid credentials"}

        user = dict(row)
        if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
            return {"ok": False, "error": "Invalid credentials"}

        # update last login
        with self._conn() as conn:
            conn.execute(
                "UPDATE users SET last_login=? WHERE id=?",
                (datetime.utcnow().isoformat(), user["id"])
            )
            conn.commit()

        token = self._generate_token(user["id"], user["workspace_id"], user["role"])
        logger.info(f"Login: {email}")
        return {
            "ok":           True,
            "token":        token,
            "user_id":      user["id"],
            "workspace_id": user["workspace_id"],
            "role":         user["role"],
            "name":         user["name"],
        }

    def verify_token(self, token: str) -> dict | None:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def get_user(self, user_id: int) -> dict | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT id, email, name, workspace_id, role, created_at, last_login "
                "FROM users WHERE id=?", (user_id,)
            ).fetchone()
        return dict(row) if row else None

    def get_workspace_users(self, workspace_id: int) -> list:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT id, email, name, role, created_at, last_login "
                "FROM users WHERE workspace_id=?", (workspace_id,)
            ).fetchall()
        return [dict(r) for r in rows]

    def invite_user(self, email: str, name: str, role: str,
                    workspace_id: int, temp_password: str = "Change@123") -> dict:
        pw_hash = bcrypt.hashpw(temp_password.encode(), bcrypt.gensalt()).decode()
        now = datetime.utcnow().isoformat()
        try:
            with self._conn() as conn:
                cur = conn.execute(
                    "INSERT INTO users (email, password_hash, name, workspace_id, role, created_at) "
                    "VALUES (?,?,?,?,?,?)",
                    (email, pw_hash, name, workspace_id, role, now)
                )
                conn.commit()
            return {"ok": True, "user_id": cur.lastrowid, "temp_password": temp_password}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def update_user_role(self, user_id: int, role: str, workspace_id: int) -> bool:
        with self._conn() as conn:
            conn.execute(
                "UPDATE users SET role=? WHERE id=? AND workspace_id=?",
                (role, user_id, workspace_id)
            )
            conn.commit()
        return True

    # ── Competitor CRUD ──────────────────────────────

    def add_competitor(self, workspace_id: int, name: str,
                       url: str = "", competitor_type: str = "brand") -> int:
        now = datetime.utcnow().isoformat()
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO competitors (workspace_id, name, url, competitor_type, created_at) "
                "VALUES (?,?,?,?,?)",
                (workspace_id, name, url, competitor_type, now)
            )
            conn.commit()
            return cur.lastrowid

    def get_competitors(self, workspace_id: int) -> list:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM competitors WHERE workspace_id=? ORDER BY id",
                (workspace_id,)
            ).fetchall()
        return [dict(r) for r in rows]

    def delete_competitor(self, competitor_id: int, workspace_id: int) -> bool:
        with self._conn() as conn:
            conn.execute(
                "DELETE FROM competitors WHERE id=? AND workspace_id=?",
                (competitor_id, workspace_id)
            )
            conn.commit()
        return True

    # ── Token ────────────────────────────────────────

    def _generate_token(self, user_id: int, workspace_id: int, role: str) -> str:
        payload = {
            "user_id":      user_id,
            "workspace_id": workspace_id,
            "role":         role,
            "exp":          datetime.utcnow() + timedelta(hours=TOKEN_HOURS),
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


# Singleton
_auth_instance = None

def get_auth() -> AuthManager:
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = AuthManager()
    return _auth_instance
