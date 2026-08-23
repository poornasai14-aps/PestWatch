"""
Stage 3 — Aggregation.

A tiny SQLite-backed spatial store that holds every pest report (species, lat,
lon, time, confidence, instance count) plus the registry of farms. This store is
the raw material for the clustering and alerting layers.
"""
from __future__ import annotations

import os
import sqlite3
import time
from typing import List, Dict, Optional

DB_PATH = os.environ.get("PESTWATCH_DB") or \
    os.path.join(os.path.dirname(__file__), "..", "data", "pestwatch.db")


def _conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                species TEXT NOT NULL,
                lat REAL NOT NULL,
                lon REAL NOT NULL,
                ts REAL NOT NULL,
                confidence REAL NOT NULL,
                instance_count INTEGER NOT NULL,
                detector_mode TEXT,
                farm_name TEXT,
                image_path TEXT
            )""")
        c.execute("""
            CREATE TABLE IF NOT EXISTS farms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                lat REAL NOT NULL,
                lon REAL NOT NULL,
                crop TEXT,
                phone TEXT
            )""")


# ----------------------------------------------------------------- reports
def add_report(species, lat, lon, confidence, instance_count,
               detector_mode="", farm_name=None, image_path=None,
               ts: Optional[float] = None) -> int:
    ts = ts if ts is not None else time.time()
    with _conn() as c:
        cur = c.execute(
            """INSERT INTO reports
               (species,lat,lon,ts,confidence,instance_count,detector_mode,farm_name,image_path)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (species, lat, lon, ts, confidence, instance_count,
             detector_mode, farm_name, image_path))
        return cur.lastrowid


def get_reports(species: Optional[str] = None,
                since_days: Optional[float] = None) -> List[Dict]:
    q = "SELECT * FROM reports WHERE 1=1"
    args: list = []
    if species:
        q += " AND species = ?"
        args.append(species)
    if since_days is not None:
        q += " AND ts >= ?"
        args.append(time.time() - since_days * 86400)
    q += " ORDER BY ts DESC"
    with _conn() as c:
        return [dict(r) for r in c.execute(q, args).fetchall()]


def species_summary() -> List[Dict]:
    with _conn() as c:
        rows = c.execute(
            "SELECT species, COUNT(*) n, MAX(ts) last FROM reports GROUP BY species"
        ).fetchall()
        return [dict(r) for r in rows]


# ------------------------------------------------------------------- farms
def add_farm(name, lat, lon, crop="", phone="") -> int:
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO farms (name,lat,lon,crop,phone) VALUES (?,?,?,?,?)",
            (name, lat, lon, crop, phone))
        return cur.lastrowid


def get_farms() -> List[Dict]:
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM farms").fetchall()]


def counts() -> Dict:
    with _conn() as c:
        r = c.execute("SELECT COUNT(*) n FROM reports").fetchone()["n"]
        f = c.execute("SELECT COUNT(*) n FROM farms").fetchone()["n"]
    return {"reports": r, "farms": f}


def reset():
    with _conn() as c:
        c.execute("DELETE FROM reports")
        c.execute("DELETE FROM farms")
