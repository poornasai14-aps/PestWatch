"""
Authentication & roles.

Two roles:
  - officer : Agriculture Department extension officer. Operates/maintains the
              system and uses the district dashboard (all clusters, all alerts,
              farm management, analytics).
  - farmer  : a registered farm owner. Reports pests and receives warnings for
              their own farm.

Kept dependency-free: PBKDF2 password hashing (stdlib hashlib) and opaque
session tokens stored in SQLite. Client sends the token as `Authorization:
Bearer <token>`.
"""
from __future__ import annotations

import hashlib
import os
import secrets
import time
from typing import Optional, Dict

from .store import _conn  # reuse the same SQLite database

PBKDF2_ROUNDS = 200_000
SESSION_TTL_DAYS = 30
ROLES = ("officer", "farmer")


# --------------------------------------------------------------- schema
def init_auth():
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT,
                role TEXT NOT NULL,
                pw_salt TEXT NOT NULL,
                pw_hash TEXT NOT NULL,
                farm_id INTEGER,
                phone TEXT,
                created REAL NOT NULL
            )""")
        c.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                expires REAL NOT NULL
            )""")


# --------------------------------------------------------------- hashing
def _hash(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), PBKDF2_ROUNDS
    ).hex()


def _verify(password: str, salt: str, expected: str) -> bool:
    return secrets.compare_digest(_hash(password, salt), expected)


# --------------------------------------------------------------- users
def create_user(username: str, password: str, role: str,
                full_name: str = "", farm_id: Optional[int] = None,
                phone: str = "") -> Dict:
    if role not in ROLES:
        raise ValueError(f"role must be one of {ROLES}")
    salt = secrets.token_hex(16)
    pw_hash = _hash(password, salt)
    with _conn() as c:
        try:
            cur = c.execute(
                """INSERT INTO users
                   (username,full_name,role,pw_salt,pw_hash,farm_id,phone,created)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (username.lower().strip(), full_name, role, salt, pw_hash,
                 farm_id, phone, time.time()))
        except Exception as e:
            raise ValueError("username already taken") from e
        return {"id": cur.lastrowid, "username": username, "role": role}


def get_user_by_name(username: str) -> Optional[Dict]:
    with _conn() as c:
        r = c.execute("SELECT * FROM users WHERE username=?",
                      (username.lower().strip(),)).fetchone()
        return dict(r) if r else None


def get_user_by_id(uid: int) -> Optional[Dict]:
    with _conn() as c:
        r = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        return dict(r) if r else None


def set_farm(username: str, farm_id: Optional[int]):
    """(Re)link a user to a farm id — used after re-seeding demo farms."""
    with _conn() as c:
        c.execute("UPDATE users SET farm_id=? WHERE username=?",
                  (farm_id, username.lower().strip()))


def public(user: Dict) -> Dict:
    """Strip secrets before sending a user to the client."""
    return {
        "id": user["id"], "username": user["username"],
        "full_name": user.get("full_name") or user["username"],
        "role": user["role"], "farm_id": user.get("farm_id"),
        "phone": user.get("phone", ""),
    }


# --------------------------------------------------------------- sessions
def login(username: str, password: str) -> Optional[Dict]:
    user = get_user_by_name(username)
    if not user or not _verify(password, user["pw_salt"], user["pw_hash"]):
        return None
    token = secrets.token_urlsafe(32)
    with _conn() as c:
        c.execute("INSERT INTO sessions (token,user_id,expires) VALUES (?,?,?)",
                  (token, user["id"], time.time() + SESSION_TTL_DAYS * 86400))
    return {"token": token, "user": public(user)}


def user_from_token(token: str) -> Optional[Dict]:
    if not token:
        return None
    with _conn() as c:
        r = c.execute("SELECT * FROM sessions WHERE token=?", (token,)).fetchone()
        if not r or r["expires"] < time.time():
            return None
        return get_user_by_id(r["user_id"])


def logout(token: str):
    with _conn() as c:
        c.execute("DELETE FROM sessions WHERE token=?", (token,))


# --------------------------------------------------------------- seeding
def seed_users(farm_id_for_farmer: Optional[int] = None):
    """Create demo accounts if none exist. Returns the credentials used."""
    init_auth()
    with _conn() as c:
        n = c.execute("SELECT COUNT(*) n FROM users").fetchone()["n"]
    if n > 0:
        return None
    create_user("officer", "officer123", "officer",
                full_name="Dist. Agri Officer (Guntur)", phone="+91 90000 00000")
    create_user("farmer", "farmer123", "farmer",
                full_name="Ravi Kumar", farm_id=farm_id_for_farmer,
                phone="+91 90000 11111")
    return {
        "officer": {"username": "officer", "password": "officer123"},
        "farmer": {"username": "farmer", "password": "farmer123"},
    }
