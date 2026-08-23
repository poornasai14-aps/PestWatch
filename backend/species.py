"""
Pest species knowledge base.

Each species carries the parameters that Layer 2 (the intelligence layer) needs:
  - base_radius_km : how far this pest typically disperses in a week. Different
                     pests move at very different speeds, so each carries its own
                     base risk radius (see overview 5.1).
  - color          : map colour for markers / clusters.
  - crop           : the crop it primarily attacks (used in the alert text).
  - inspect        : where on the plant the farmer should look.
  - action         : recommended control measure (the "what to do" in an alert).

This file is intentionally the single source of truth for pest behaviour so the
detector, the clustering, and the alerting layer all agree on the same species.
"""

SPECIES = {
    "fall_armyworm": {
        "label": "Fall Armyworm",
        "crop": "Maize",
        "base_radius_km": 3.5,
        "color": "#e63946",
        "inspect": "Inspect the whorls and new leaves of your maize today.",
        "action": "Apply Emamectin benzoate 5% SG or Spinetoram; hand-pick egg masses.",
    },
    "aphid": {
        "label": "Aphid Colony",
        "crop": "Multiple",
        "base_radius_km": 2.0,
        "color": "#2a9d8f",
        "inspect": "Check the undersides of young leaves and growing tips.",
        "action": "Spray Imidacloprid 17.8% SL or release ladybird beetles.",
    },
    "stem_borer": {
        "label": "Stem Borer",
        "crop": "Rice",
        "base_radius_km": 2.5,
        "color": "#f4a261",
        "inspect": "Look for dead-hearts and bore holes in the stem near the base.",
        "action": "Apply Cartap hydrochloride 4G; remove and destroy affected tillers.",
    },
    "whitefly": {
        "label": "Whitefly",
        "crop": "Cotton",
        "base_radius_km": 4.0,
        "color": "#8338ec",
        "inspect": "Shake the plant — clouds of tiny white flies rise from the leaf underside.",
        "action": "Spray Diafenthiuron 50% WP; install yellow sticky traps.",
    },
    "leaf_folder": {
        "label": "Rice Leaf Folder",
        "crop": "Rice",
        "base_radius_km": 2.2,
        "color": "#3a86ff",
        "inspect": "Look for folded leaves with white streaks where larvae have scraped.",
        "action": "Spray Chlorantraniliprole 0.4% GR; avoid excess nitrogen.",
    },
    "pink_bollworm": {
        "label": "Pink Bollworm",
        "crop": "Cotton",
        "base_radius_km": 3.0,
        "color": "#ff006e",
        "inspect": "Open a few bolls — look for pink larvae and rosetted flowers.",
        "action": "Install pheromone traps (5/acre); spray Thiodicarb 75% WP.",
    },
    "thrips": {
        "label": "Thrips",
        "crop": "Chilli",
        "base_radius_km": 2.8,
        "color": "#ffbe0b",
        "inspect": "Check for curled, silvery leaves and scarring on tender growth.",
        "action": "Spray Fipronil 5% SC; use blue sticky traps.",
    },
    "mealybug": {
        "label": "Mealybug",
        "crop": "Cotton",
        "base_radius_km": 1.8,
        "color": "#fb5607",
        "inspect": "Look for white cottony masses at leaf axils and stem nodes.",
        "action": "Spray Buprofezin 25% SC; remove heavily infested plant parts.",
    },
    "jassid": {
        "label": "Jassid (Leafhopper)",
        "crop": "Cotton",
        "base_radius_km": 2.6,
        "color": "#06d6a0",
        "inspect": "Leaf margins yellow then turn brick-red and curl downward.",
        "action": "Spray Thiamethoxam 25% WG; maintain field sanitation.",
    },
    # --- additional species that the trained (Francesco/pests-2xlvx) model emits ---
    "planthopper": {
        "label": "Planthopper (BPH/WBPH)",
        "crop": "Rice",
        "base_radius_km": 3.2,
        "color": "#00b4d8",
        "inspect": "Part the crop at the base — look for hoppers and 'hopper burn' patches.",
        "action": "Spray Pymetrozine 50% WG; drain the field for a few days; avoid excess nitrogen.",
    },
    "cutworm": {
        "label": "Cutworm (Agrotis)",
        "crop": "Multiple",
        "base_radius_km": 2.3,
        "color": "#9d4edd",
        "inspect": "Look for seedlings cut at the base at night; dig near the collar to find curled larvae.",
        "action": "Apply Chlorpyriphos poison bait in the evening; keep field weed-free.",
    },
    "mole_cricket": {
        "label": "Mole Cricket",
        "crop": "Rice/Nursery",
        "base_radius_km": 2.0,
        "color": "#b5838d",
        "inspect": "Look for surface tunnels and uprooted seedlings in nursery beds.",
        "action": "Flood the nursery; apply Fipronil granules along tunnels.",
    },
    "webworm": {
        "label": "Webworm (Loxostege/Spoladea)",
        "crop": "Vegetables/Beet",
        "base_radius_km": 2.6,
        "color": "#e07a5f",
        "inspect": "Look for webbed, skeletonised leaves with larvae inside the webbing.",
        "action": "Spray Emamectin benzoate 5% SG; remove webbed leaves.",
    },
    "pod_borer": {
        "label": "Pod/Leaf Borer",
        "crop": "Legumes",
        "base_radius_km": 2.7,
        "color": "#f77f00",
        "inspect": "Look for bore holes in pods/flowers and larvae feeding inside.",
        "action": "Install pheromone traps; spray Chlorantraniliprole 18.5% SC.",
    },
    "white_grub": {
        "label": "White Grub (beetle)",
        "crop": "Multiple",
        "base_radius_km": 2.1,
        "color": "#c9ada7",
        "inspect": "Wilting plants; dig near roots to find C-shaped white grubs.",
        "action": "Apply Imidacloprid soil drench; collect adult beetles at dusk.",
    },
    "other_moth": {
        "label": "Moth / Caterpillar pest",
        "crop": "Multiple",
        "base_radius_km": 2.5,
        "color": "#ef476f",
        "inspect": "Inspect leaves and growing points for caterpillars and feeding damage.",
        "action": "Identify precisely, then apply the recommended larvicide; use pheromone traps to monitor.",
    },
    "beneficial": {
        "label": "Beneficial insect (no action)",
        "crop": "-",
        "base_radius_km": 0.0,
        "color": "#52b788",
        "inspect": "This is a predator/indicator species — it helps control pests.",
        "action": "Do NOT spray. Conserve natural enemies.",
    },
    "healthy": {
        "label": "Healthy / No pest",
        "crop": "-",
        "base_radius_km": 0.0,
        "color": "#94a3b8",
        "inspect": "No action needed. Keep monitoring.",
        "action": "No treatment required.",
    },
}

# Maps the 29 scientific class names from the Francesco/pests-2xlvx model onto
# our farmer-facing knowledge base, so a detection yields real advice + sensible
# outbreak grouping. Unlisted names fall back to a generic pest record.
DATASET_TO_KB = {
    "pests": "other_moth",
    "agrotis": "cutworm",
    "athetis lepigone": "other_moth",
    "athetis lineosa": "other_moth",
    "chilo suppressalis": "stem_borer",
    "cnaphalocrocis medinalis guenee": "leaf_folder",
    "creatonotus transiens": "other_moth",
    "diaphania indica": "leaf_folder",
    "endotricha consocia": "other_moth",
    "euproctis sparsa": "other_moth",
    "gryllidae": "cutworm",
    "gryllotalpidae": "mole_cricket",
    "helicoverpa armigera": "pod_borer",
    "holotrichia oblita faldermann": "white_grub",
    "loxostege sticticalis": "webworm",
    "mamestra brassicae": "other_moth",
    "maruca testulalis geyer": "pod_borer",
    "mythimna separata": "fall_armyworm",
    "naranga aenescens moore": "other_moth",
    "nilaparvata": "planthopper",
    "paracymoriza taiwanalis": "other_moth",
    "sesamia inferens": "stem_borer",
    "sirthenea flavipes": "beneficial",
    "sogatella furcifera": "planthopper",
    "spodoptera exigua": "fall_armyworm",
    "spoladea recurvalis": "webworm",
    "staurophora celsia": "other_moth",
    "timandra recompta": "other_moth",
    "trichoptera": "beneficial",
}


def resolve_dataset_name(name: str) -> str:
    """Scientific class name (from the trained model) -> knowledge-base key."""
    key = name.strip().lower()
    if key in DATASET_TO_KB:
        return DATASET_TO_KB[key]
    slug = key.replace(" ", "_").replace("-", "_")
    return slug if slug in SPECIES else "other_moth"

# Ordered list of the pest classes a detector is expected to output (excludes
# "healthy"). Used to map arbitrary detector class indices onto our knowledge base.
PEST_CLASSES = [k for k in SPECIES.keys() if k != "healthy"]


# Telugu translations (label / inspect / action). Chemical names stay in English.
SPECIES_TE = {
    "fall_armyworm": {"label": "సైనిక పురుగు (Fall Armyworm)",
        "inspect": "మొక్కజొన్న సుడులు, కొత్త ఆకులను ఈరోజే పరిశీలించండి.",
        "action": "Emamectin benzoate 5% SG లేదా Spinetoram పిచికారీ చేయండి; గుడ్ల సముదాయాలను చేతితో తీసివేయండి."},
    "aphid": {"label": "పేను (Aphid)",
        "inspect": "లేత ఆకుల అడుగుభాగం, చిగుళ్లను పరిశీలించండి.",
        "action": "Imidacloprid 17.8% SL పిచికారీ చేయండి లేదా లేడీబర్డ్ బీటిల్స్ వదలండి."},
    "stem_borer": {"label": "కాండం తొలిచే పురుగు",
        "inspect": "కాండం అడుగున డెడ్-హార్ట్స్, రంధ్రాల కోసం చూడండి.",
        "action": "Cartap hydrochloride 4G వేయండి; దెబ్బతిన్న పిలకలను తీసివేసి నాశనం చేయండి."},
    "whitefly": {"label": "తెల్లదోమ (Whitefly)",
        "inspect": "మొక్కను కదిలిస్తే ఆకు అడుగు నుండి చిన్న తెల్ల ఈగలు లేస్తాయి.",
        "action": "Diafenthiuron 50% WP పిచికారీ చేయండి; పసుపు జిగురు ఉచ్చులు అమర్చండి."},
    "leaf_folder": {"label": "ఆకు ముడత పురుగు",
        "inspect": "లార్వా గీసిన తెల్లని చారలతో ముడుచుకున్న ఆకుల కోసం చూడండి.",
        "action": "Chlorantraniliprole 0.4% GR పిచికారీ చేయండి; అధిక నత్రజని నివారించండి."},
    "pink_bollworm": {"label": "గులాబీ కాయతొలుచు పురుగు",
        "inspect": "కొన్ని కాయలు తెరిచి — గులాబీ లార్వా, రోసెట్ పూల కోసం చూడండి.",
        "action": "ఫెరమోన్ ఉచ్చులు (5/ఎకరం) అమర్చండి; Thiodicarb 75% WP పిచికారీ చేయండి."},
    "thrips": {"label": "తామర పురుగు (Thrips)",
        "inspect": "ముడుచుకున్న, వెండి రంగు ఆకులు, లేత భాగాలపై గీతల కోసం చూడండి.",
        "action": "Fipronil 5% SC పిచికారీ చేయండి; నీలి జిగురు ఉచ్చులు వాడండి."},
    "mealybug": {"label": "పిండి నల్లి (Mealybug)",
        "inspect": "ఆకు సందుల్లో, కాండం కణుపుల వద్ద తెల్లని దూది వంటి గుంపుల కోసం చూడండి.",
        "action": "Buprofezin 25% SC పిచికారీ చేయండి; ఎక్కువగా సోకిన భాగాలను తీసివేయండి."},
    "jassid": {"label": "పచ్చదోమ (Jassid)",
        "inspect": "ఆకు అంచులు పసుపు నుండి ఇటుక-ఎరుపుగా మారి కిందికి ముడుచుకుంటాయి.",
        "action": "Thiamethoxam 25% WG పిచికారీ చేయండి; పొల పరిశుభ్రత పాటించండి."},
    "planthopper": {"label": "సుడిదోమ (Planthopper)",
        "inspect": "మొక్క అడుగున దోమలు, 'హాపర్ బర్న్' మచ్చల కోసం చూడండి.",
        "action": "Pymetrozine 50% WG పిచికారీ చేయండి; కొన్ని రోజులు నీరు తీసేయండి."},
    "cutworm": {"label": "కట్‌వార్మ్ పురుగు",
        "inspect": "రాత్రిపూట అడుగున కత్తిరించిన మొలకల కోసం చూడండి; మెడ దగ్గర తవ్వి లార్వా చూడండి.",
        "action": "సాయంత్రం Chlorpyriphos విష ఎర వేయండి; పొలం కలుపు లేకుండా ఉంచండి."},
    "mole_cricket": {"label": "మోల్ క్రికెట్",
        "inspect": "నర్సరీలో ఉపరితల సొరంగాలు, పెకిలించిన మొలకల కోసం చూడండి.",
        "action": "నర్సరీని ముంచెత్తండి; సొరంగాల వెంట Fipronil గుళికలు వేయండి."},
    "webworm": {"label": "వెబ్‌వార్మ్ పురుగు",
        "inspect": "గూడు కట్టిన, అస్థిపంజరమైన ఆకుల కోసం చూడండి.",
        "action": "Emamectin benzoate 5% SG పిచికారీ చేయండి; గూడు ఆకులను తీసివేయండి."},
    "pod_borer": {"label": "కాయ/ఆకు తొలిచే పురుగు",
        "inspect": "కాయలు/పూలలో రంధ్రాలు, లోపల లార్వా కోసం చూడండి.",
        "action": "ఫెరమోన్ ఉచ్చులు అమర్చండి; Chlorantraniliprole 18.5% SC పిచికారీ చేయండి."},
    "white_grub": {"label": "తెల్ల గొంగళి (White Grub)",
        "inspect": "వాడిన మొక్కలు; వేర్ల దగ్గర తవ్వి C-ఆకారపు తెల్ల గొంగళి చూడండి.",
        "action": "Imidacloprid మట్టిలో వేయండి; సాయంత్రం బీటిల్స్ సేకరించండి."},
    "other_moth": {"label": "చిమ్మెట/గొంగళి పురుగు",
        "inspect": "ఆకులు, చిగుళ్లపై గొంగళి పురుగులు, తినివేసిన గుర్తుల కోసం చూడండి.",
        "action": "సరిగా గుర్తించి తగిన మందు పిచికారీ చేయండి; ఫెరమోన్ ఉచ్చులతో పర్యవేక్షించండి."},
    "beneficial": {"label": "ఉపయోగకరమైన కీటకం (చర్య వద్దు)",
        "inspect": "ఇది పురుగులను నియంత్రించే మిత్ర కీటకం.",
        "action": "పిచికారీ చేయవద్దు. మిత్ర కీటకాలను కాపాడండి."},
    "healthy": {"label": "ఆరోగ్యకరం / పురుగు లేదు",
        "inspect": "చర్య అవసరం లేదు. పర్యవేక్షిస్తూ ఉండండి.",
        "action": "చికిత్స అవసరం లేదు."},
}


def get(species_key: str, lang: str = "en") -> dict:
    """Return the species record, localized, falling back to a generic pest."""
    if species_key in SPECIES:
        rec = {"key": species_key, **SPECIES[species_key]}
    else:
        rec = {
            "key": species_key,
            "label": species_key.replace("_", " ").title(),
            "crop": "Unknown",
            "base_radius_km": 2.5,
            "color": "#e63946",
            "inspect": "Inspect the affected crop parts closely.",
            "action": "Consult your local agricultural extension officer.",
        }
    if lang == "te" and species_key in SPECIES_TE:
        rec = {**rec, **SPECIES_TE[species_key]}
    return rec
