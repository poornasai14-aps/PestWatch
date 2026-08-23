"""
Seed the store with a realistic demo scenario around Guntur, Andhra Pradesh
(a real, intensive agriculture district). Gives the demo an immediate outbreak
to show, plus registered farms sitting in the projected risk ring.
"""
from __future__ import annotations

import random
import time

from . import store

# Guntur region centre
BASE_LAT, BASE_LON = 16.3067, 80.4365


def _jitter(lat, lon, km):
    # ~1 deg lat ~= 111 km; spread within `km` radius
    dlat = (random.uniform(-1, 1) * km) / 111.0
    dlon = (random.uniform(-1, 1) * km) / (111.0 * 0.96)
    return lat + dlat, lon + dlon


def seed(reset: bool = True):
    store.init_db()
    if reset:
        store.reset()
    now = time.time()
    random.seed(42)

    # --- Cluster 1: Fall armyworm forming NE of Guntur (fresh, growing) ------
    c1_lat, c1_lon = BASE_LAT + 0.06, BASE_LON + 0.05
    for i in range(7):
        lat, lon = _jitter(c1_lat, c1_lon, 1.4)
        store.add_report("fall_armyworm", lat, lon,
                         confidence=round(random.uniform(0.7, 0.95), 3),
                         instance_count=random.randint(2, 6),
                         detector_mode="seed",
                         ts=now - random.uniform(0, 4) * 86400)

    # --- Cluster 2: Whitefly on cotton, SW, slightly older -------------------
    c2_lat, c2_lon = BASE_LAT - 0.05, BASE_LON - 0.06
    for i in range(5):
        lat, lon = _jitter(c2_lat, c2_lon, 1.6)
        store.add_report("whitefly", lat, lon,
                         confidence=round(random.uniform(0.6, 0.9), 3),
                         instance_count=random.randint(3, 8),
                         detector_mode="seed",
                         ts=now - random.uniform(2, 6) * 86400)

    # --- Scattered single reports (noise, should NOT form clusters) ----------
    for sp in ["aphid", "stem_borer", "thrips"]:
        lat, lon = _jitter(BASE_LAT, BASE_LON, 8)
        store.add_report(sp, lat, lon,
                         confidence=round(random.uniform(0.5, 0.8), 3),
                         instance_count=random.randint(1, 3),
                         detector_mode="seed",
                         ts=now - random.uniform(0, 5) * 86400)

    # --- Registered farms: some in the armyworm risk ring, some clear --------
    farms = [
        # inside the armyworm cluster footprint -> gets a 'confirmation' alert
        ("Ravi's Maize Farm",   c1_lat + 0.006, c1_lon + 0.004, "Maize",  "+91 90000 11111"),
        # in the outer risk ring -> 'warning' alerts, at increasing distance
        ("Lakshmi Agro",        c1_lat + 0.03,  c1_lon + 0.02,  "Maize",  "+91 90000 22222"),
        ("Sri Venkatesa Farm",  c1_lat + 0.05,  c1_lon - 0.03,  "Maize",  "+91 90000 33333"),
        # inside the whitefly cluster/ring
        ("Guntur Cotton Estate",c2_lat + 0.01,  c2_lon - 0.008, "Cotton", "+91 90000 44444"),
        # safely clear of any outbreak -> stays blue, no alert
        ("Krishna Fields",      BASE_LAT + 0.22, BASE_LON + 0.24, "Rice",  "+91 90000 55555"),
        ("Anand Organic Farm",  BASE_LAT - 0.27, BASE_LON + 0.22, "Chilli","+91 90000 66666"),
    ]
    for name, lat, lon, crop, phone in farms:
        store.add_farm(name, lat, lon, crop, phone)

    return store.counts()


if __name__ == "__main__":
    print(seed())
