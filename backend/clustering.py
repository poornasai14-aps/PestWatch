"""
Stage 4 + 5 — the intelligence layer (this is what makes the project ours).

  Stage 4  Cluster analysis   : DBSCAN over report coordinates, per species,
                                within a rolling time window -> outbreak clusters.
  Stage 5  Risk projection     : project a risk radius around each cluster centroid
                                that scales with species dispersal, cluster
                                intensity and recency.
  Stage 5  Alerting            : match registered farms against the risk radius and
                                generate a concrete, four-question alert per farm.
"""
from __future__ import annotations

import math
import time
from typing import List, Dict

import numpy as np
from sklearn.cluster import DBSCAN

from . import species as species_kb
from .geo import haversine_km, bearing_deg, compass

# DBSCAN parameters. eps is expressed in kilometres and converted to radians for
# the haversine metric so clustering is correct on the sphere.
DEFAULT_EPS_KM = 2.5
DEFAULT_MIN_SAMPLES = 3
DEFAULT_WINDOW_DAYS = 7.0
EARTH_R_KM = 6371.0088


def _cluster_one_species(reports: List[Dict], eps_km: float,
                         min_samples: int) -> List[Dict]:
    """Run DBSCAN on a single species' reports; return outbreak clusters."""
    if len(reports) < min_samples:
        return []
    coords = np.radians([[r["lat"], r["lon"]] for r in reports])
    db = DBSCAN(eps=eps_km / EARTH_R_KM, min_samples=min_samples,
                metric="haversine", algorithm="ball_tree").fit(coords)

    clusters = []
    for label in set(db.labels_):
        if label == -1:
            continue  # noise
        members = [reports[i] for i in range(len(reports)) if db.labels_[i] == label]
        clusters.append(_summarise_cluster(members))
    return clusters


def _summarise_cluster(members: List[Dict]) -> Dict:
    lats = [m["lat"] for m in members]
    lons = [m["lon"] for m in members]
    clat, clon = float(np.mean(lats)), float(np.mean(lons))

    # geographic radius of the cluster itself (max member distance to centroid)
    radius_km = max((haversine_km(clat, clon, m["lat"], m["lon"]) for m in members),
                    default=0.0)

    now = time.time()
    last_ts = max(m["ts"] for m in members)
    ages_days = [(now - m["ts"]) / 86400 for m in members]
    mean_age = float(np.mean(ages_days))
    newest_age = min(ages_days)

    species = members[0]["species"]
    return {
        "species": species,
        "label": species_kb.get(species)["label"],
        "color": species_kb.get(species)["color"],
        "centroid": {"lat": clat, "lon": clon},
        "cluster_radius_km": round(radius_km, 2),
        "report_count": len(members),
        "total_instances": int(sum(m.get("instance_count", 1) for m in members)),
        "mean_age_days": round(mean_age, 1),
        "newest_age_days": round(newest_age, 1),
        "last_report_ts": last_ts,
        "members": members,
    }


def project_risk_radius(cluster: Dict) -> float:
    """
    Risk radius (km) = base species dispersal radius, scaled by:
      - intensity : more, denser reports -> wider projection
      - recency   : clusters that grew recently project further
    (overview 5.1). Returns a radius always >= the cluster's own footprint.
    """
    base = species_kb.get(cluster["species"])["base_radius_km"]
    if base <= 0:
        return 0.0

    # intensity: log-scaled with report count, so it grows but saturates.
    intensity = 1.0 + 0.35 * math.log2(max(cluster["report_count"], 1))

    # recency: a cluster whose newest report is today projects at full strength;
    # one that has been static for a week shrinks toward 0.6x.
    newest = cluster["newest_age_days"]
    recency = max(0.6, 1.3 - 0.1 * newest)

    radius = base * intensity * recency
    return round(max(radius, cluster["cluster_radius_km"] + 0.5), 2)


def build_clusters(reports: List[Dict], eps_km=DEFAULT_EPS_KM,
                   min_samples=DEFAULT_MIN_SAMPLES,
                   window_days=DEFAULT_WINDOW_DAYS) -> List[Dict]:
    """Cluster all reports (rolling window) grouped by species; attach risk radius."""
    cutoff = time.time() - window_days * 86400
    recent = [r for r in reports if r["ts"] >= cutoff]

    by_species: Dict[str, List[Dict]] = {}
    for r in recent:
        if r["species"] == "healthy":
            continue
        by_species.setdefault(r["species"], []).append(r)

    clusters = []
    for sp, rs in by_species.items():
        for cl in _cluster_one_species(rs, eps_km, min_samples):
            cl["risk_radius_km"] = project_risk_radius(cl)
            cl["severity"] = _severity(cl)
            clusters.append(cl)
    # strongest first
    clusters.sort(key=lambda c: (c["report_count"], -c["newest_age_days"]),
                  reverse=True)
    return clusters


def _severity(cluster: Dict) -> str:
    score = cluster["report_count"] + cluster["total_instances"] * 0.3
    if cluster["newest_age_days"] <= 2:
        score += 3
    if score >= 12:
        return "critical"
    if score >= 7:
        return "high"
    return "moderate"


# ----------------------------------------------------------------- alerting
_COMPASS_TE = {"N": "ఉత్తరం", "NE": "ఈశాన్యం", "E": "తూర్పు", "SE": "ఆగ్నేయం",
               "S": "దక్షిణం", "SW": "నైరుతి", "W": "పడమర", "NW": "వాయవ్యం"}


def generate_alerts(clusters: List[Dict], farms: List[Dict], lang: str = "en") -> List[Dict]:
    """
    For every cluster, find farms inside the risk radius and produce an alert.
    Farms already inside the cluster footprint get a 'confirmation' message;
    farms in the outer ring get a 'warning' with distance, direction and lead time.
    Localised to English or Telugu.
    """
    alerts = []
    for cl in clusters:
        clat = cl["centroid"]["lat"]
        clon = cl["centroid"]["lon"]
        sp = species_kb.get(cl["species"], lang)
        for farm in farms:
            d = haversine_km(clat, clon, farm["lat"], farm["lon"])
            if d > cl["risk_radius_km"]:
                continue

            inside_cluster = d <= cl["cluster_radius_km"]
            brg = bearing_deg(farm["lat"], farm["lon"], clat, clon)
            direction = compass(brg)
            dir_disp = _COMPASS_TE.get(direction, direction) if lang == "te" else direction
            days = max(int(round(cl["mean_age_days"])), 1)
            edge_km = round(d - cl["cluster_radius_km"], 1)

            if inside_cluster:
                kind = "confirmation"
                if lang == "te":
                    headline = (f"{sp['label']} వ్యాప్తి మీ ప్రాంతంలో నిర్ధారించబడింది "
                                f"({cl['report_count']} నివేదికలు).")
                else:
                    headline = (f"{sp['label']} outbreak confirmed around your area "
                                f"({cl['report_count']} reports).")
            else:
                kind = "warning"
                if lang == "te":
                    headline = (f"{sp['label']} {round(d,1)} కి.మీ {dir_disp} దిశలో "
                                f"నిర్ధారించబడింది. గత {days} రోజుల్లో {cl['report_count']} నివేదికలు. "
                                f"వ్యాప్తి అంచు ~{edge_km} కి.మీ దూరంలో.")
                else:
                    headline = (f"{sp['label']} confirmed {round(d,1)} km {direction}. "
                                f"{cl['report_count']} reports in the last {days} days. "
                                f"Outbreak edge ~{edge_km} km away.")

            alerts.append({
                "farm": farm["name"],
                "farm_lat": farm["lat"],
                "farm_lon": farm["lon"],
                "farm_phone": farm.get("phone", ""),
                "species": cl["species"],
                "species_label": sp["label"],
                "kind": kind,
                "severity": cl["severity"],
                "distance_km": round(d, 2),
                "direction": dir_disp,
                "lead_days_est": _lead_time_estimate(d, cl),
                "headline": headline,
                "inspect": sp["inspect"],
                "action": sp["action"],
                "cluster_centroid": cl["centroid"],
            })

    # nearest / most severe first
    sev_rank = {"critical": 0, "high": 1, "moderate": 2}
    alerts.sort(key=lambda a: (sev_rank.get(a["severity"], 3), a["distance_km"]))
    return alerts


def _lead_time_estimate(distance_km: float, cluster: Dict) -> float:
    """
    Rough lead time (days) before the front reaches a farm: distance to the
    cluster edge divided by an assumed dispersal speed derived from the species
    base radius over the time window. Purely proximity-based (a stated limit).
    """
    edge_dist = max(distance_km - cluster["cluster_radius_km"], 0.0)
    base = species_kb.get(cluster["species"])["base_radius_km"] or 2.5
    speed_km_per_day = max(base / 7.0, 0.15)   # base radius spread over ~1 week
    return round(edge_dist / speed_km_per_day, 1)
