"""
Leaf-disease knowledge base — advice for every class the disease classifier
emits (full PlantVillage: 38 classes across 14 crops). Mirrors species.py but
for plant diseases (fungal/bacterial/viral leaf problems), a different problem
from insect pests.

Keys MUST match the ImageFolder class names created by prepare_disease.py.
"""

_H = "No disease detected. Keep monitoring."   # healthy note
_HG = "#2d6a4f"                                 # healthy colour
_D = "#c1121f"                                  # diseased colour


def _healthy(label, crop):
    return {"label": label, "crop": crop, "healthy": True, "color": _HG,
            "note": _H, "action": "No treatment needed."}


def _dz(label, crop, note, action, color=_D):
    return {"label": label, "crop": crop, "healthy": False, "color": color,
            "note": note, "action": action}


DISEASES = {
    # ---- Apple
    "apple_scab": _dz("Apple Scab", "Apple",
        "Olive-green to brown velvety spots on leaves and fruit (fungus).",
        "Spray Captan or Mancozeb; prune for airflow; remove fallen leaves."),
    "apple_black_rot": _dz("Apple Black Rot", "Apple",
        "Purple-bordered 'frog-eye' leaf spots; rotting fruit (fungus).",
        "Remove mummified fruit and cankers; spray Thiophanate-methyl."),
    "apple_cedar_rust": _dz("Cedar Apple Rust", "Apple",
        "Bright orange-yellow spots on the upper leaf surface (fungus).",
        "Apply Myclobutanil; remove nearby juniper/cedar hosts."),
    "apple_healthy": _healthy("Apple — Healthy", "Apple"),
    # ---- Blueberry
    "blueberry_healthy": _healthy("Blueberry — Healthy", "Blueberry"),
    # ---- Cherry
    "cherry_powdery_mildew": _dz("Cherry Powdery Mildew", "Cherry",
        "White powdery fungal coating on leaves and shoots.",
        "Spray wettable sulphur or Myclobutanil; improve air circulation."),
    "cherry_healthy": _healthy("Cherry — Healthy", "Cherry"),
    # ---- Corn / Maize
    "corn_gray_leaf_spot": _dz("Corn Gray Leaf Spot", "Maize",
        "Rectangular grey-tan lesions running along leaf veins (fungus).",
        "Rotate crops; use resistant hybrids; spray Azoxystrobin if severe."),
    "corn_common_rust": _dz("Corn Common Rust", "Maize",
        "Small cinnamon-brown pustules on both leaf surfaces (fungus).",
        "Plant resistant hybrids; apply Propiconazole at early infection."),
    "corn_northern_blight": _dz("Corn Northern Leaf Blight", "Maize",
        "Long grey-green cigar-shaped lesions on leaves (fungus).",
        "Use resistant hybrids; rotate; spray Mancozeb/Azoxystrobin if needed."),
    "corn_healthy": _healthy("Corn — Healthy", "Maize"),
    # ---- Grape
    "grape_black_rot": _dz("Grape Black Rot", "Grape",
        "Tan leaf spots with dark borders; black shrivelled berries (fungus).",
        "Spray Mancozeb/Myclobutanil; remove mummified berries and infected canes."),
    "grape_esca": _dz("Grape Esca (Black Measles)", "Grape",
        "Tiger-stripe leaf pattern; dark spots on berries (fungal complex).",
        "Prune and destroy affected wood; protect pruning wounds; no full cure."),
    "grape_leaf_blight": _dz("Grape Leaf Blight (Isariopsis)", "Grape",
        "Irregular brown angular leaf spots that merge (fungus).",
        "Spray copper fungicide; improve canopy airflow; remove debris."),
    "grape_healthy": _healthy("Grape — Healthy", "Grape"),
    # ---- Orange
    "orange_citrus_greening": _dz("Citrus Greening (HLB)", "Orange",
        "Blotchy yellow mottling; lopsided bitter fruit (bacterial, insect-spread).",
        "No cure — remove infected trees; control the psyllid vector."),
    # ---- Peach
    "peach_bacterial_spot": _dz("Peach Bacterial Spot", "Peach",
        "Small dark angular leaf spots; cracked fruit (bacteria).",
        "Spray copper/oxytetracycline; plant resistant varieties."),
    "peach_healthy": _healthy("Peach — Healthy", "Peach"),
    # ---- Pepper (bell)
    "pepper_bacterial_spot": _dz("Pepper Bacterial Spot", "Bell Pepper",
        "Water-soaked spots turning brown with yellow halos (bacteria).",
        "Use certified seed; spray copper+Mancozeb; avoid overhead watering."),
    "pepper_healthy": _healthy("Bell Pepper — Healthy", "Bell Pepper"),
    # ---- Potato
    "potato_early_blight": _dz("Potato Early Blight", "Potato",
        "Concentric-ring 'target' spots on lower leaves (fungus).",
        "Spray Chlorothalonil/Mancozeb; avoid overhead irrigation."),
    "potato_late_blight": _dz("Potato Late Blight", "Potato",
        "Water-soaked dark lesions with white mould edge — spreads fast (oomycete).",
        "Spray Cymoxanil+Mancozeb urgently; destroy infected plants."),
    "potato_healthy": _healthy("Potato — Healthy", "Potato"),
    # ---- Raspberry / Soybean
    "raspberry_healthy": _healthy("Raspberry — Healthy", "Raspberry"),
    "soybean_healthy": _healthy("Soybean — Healthy", "Soybean"),
    # ---- Squash
    "squash_powdery_mildew": _dz("Squash Powdery Mildew", "Squash",
        "White powdery patches on leaves and stems (fungus).",
        "Spray sulphur or potassium bicarbonate; remove worst leaves."),
    # ---- Strawberry
    "strawberry_leaf_scorch": _dz("Strawberry Leaf Scorch", "Strawberry",
        "Numerous small purple spots that merge, scorching the leaf (fungus).",
        "Renovate beds; spray Captan; improve airflow and drainage."),
    "strawberry_healthy": _healthy("Strawberry — Healthy", "Strawberry"),
    # ---- Tomato
    "tomato_bacterial_spot": _dz("Tomato Bacterial Spot", "Tomato",
        "Small dark greasy spots with yellow halos on leaves and fruit (bacteria).",
        "Use certified seed; spray copper+Mancozeb; rotate crops."),
    "tomato_early_blight": _dz("Tomato Early Blight", "Tomato",
        "Concentric-ring target spots on older leaves (fungus).",
        "Spray Chlorothalonil/Mancozeb; mulch; remove lower leaves."),
    "tomato_late_blight": _dz("Tomato Late Blight", "Tomato",
        "Dark greasy blotches on leaves and stems — spreads fast (oomycete).",
        "Spray Cymoxanil+Mancozeb urgently; remove infected foliage."),
    "tomato_leaf_mold": _dz("Tomato Leaf Mold", "Tomato",
        "Yellow blotches on top, olive-green mould underneath (fungus).",
        "Improve ventilation; reduce humidity; spray Chlorothalonil."),
    "tomato_septoria_spot": _dz("Tomato Septoria Leaf Spot", "Tomato",
        "Many small circular spots with dark borders and grey centres (fungus).",
        "Remove infected leaves; spray Mancozeb; avoid wetting foliage."),
    "tomato_spider_mites": _dz("Tomato Spider Mites", "Tomato",
        "Fine stippling/yellowing with webbing on leaf undersides (mite).",
        "Spray Abamectin or wettable sulphur; encourage predatory mites."),
    "tomato_target_spot": _dz("Tomato Target Spot", "Tomato",
        "Brown spots with concentric rings on leaves and fruit (fungus).",
        "Spray Azoxystrobin/Chlorothalonil; improve airflow."),
    "tomato_yellow_leaf_curl_virus": _dz("Tomato Yellow Leaf Curl Virus", "Tomato",
        "Upward-curling yellow leaves; stunted plant (virus, whitefly-spread).",
        "No cure — remove infected plants; control whitefly; use resistant varieties."),
    "tomato_mosaic_virus": _dz("Tomato Mosaic Virus", "Tomato",
        "Mottled light/dark green leaves, distorted growth (virus).",
        "No cure — remove infected plants; disinfect tools; use resistant seed."),
    "tomato_healthy": _healthy("Tomato — Healthy", "Tomato"),
}


# Telugu translations (label / note / action). Chemical names stay in English.
_NT = "వ్యాధి లేదు."
_AT = "చికిత్స అవసరం లేదు."
DISEASES_TE = {
    "apple_scab": ("యాపిల్ స్కాబ్", "ఆకులు, పండ్లపై ఆలివ్-గోధుమ మెత్తని మచ్చలు (శిలీంధ్రం).", "Captan లేదా Mancozeb పిచికారీ; గాలి కోసం కత్తిరించండి; రాలిన ఆకులు తీసివేయండి."),
    "apple_black_rot": ("యాపిల్ బ్లాక్ రాట్", "ఊదా అంచుగల 'కప్ప-కన్ను' మచ్చలు; కుళ్ళిన పండ్లు.", "కుళ్ళిన పండ్లు, కాంకర్లు తీసివేయండి; Thiophanate-methyl పిచికారీ."),
    "apple_cedar_rust": ("సీడార్ యాపిల్ రస్ట్", "ఆకు పైభాగంలో ప్రకాశవంతమైన నారింజ-పసుపు మచ్చలు.", "Myclobutanil వేయండి; సమీపంలోని జునిపర్/సీడార్ తీసివేయండి."),
    "apple_healthy": ("యాపిల్ — ఆరోగ్యకరం", _NT, _AT),
    "blueberry_healthy": ("బ్లూబెర్రీ — ఆరోగ్యకరం", _NT, _AT),
    "cherry_powdery_mildew": ("చెర్రీ బూడిద తెగులు", "ఆకులు, చిగుళ్లపై తెల్లని బూడిద పొర (శిలీంధ్రం).", "సల్ఫర్ లేదా Myclobutanil పిచికారీ; గాలి ప్రసరణ మెరుగుపరచండి."),
    "cherry_healthy": ("చెర్రీ — ఆరోగ్యకరం", _NT, _AT),
    "corn_gray_leaf_spot": ("మొక్కజొన్న బూడిద ఆకు మచ్చ", "ఆకు ఈనెల వెంట దీర్ఘచతురస్ర బూడిద-గోధుమ మచ్చలు.", "పంట మార్పిడి; నిరోధక రకాలు; తీవ్రంగా ఉంటే Azoxystrobin."),
    "corn_common_rust": ("మొక్కజొన్న రస్ట్", "ఆకు రెండువైపులా చిన్న దాల్చినచెక్క-గోధుమ బొబ్బలు.", "నిరోధక రకాలు నాటండి; Propiconazole వేయండి."),
    "corn_northern_blight": ("మొక్కజొన్న ఉత్తర ఆకు మాడు", "ఆకులపై పొడవైన బూడిద-ఆకుపచ్చ చుట్ట ఆకారపు మచ్చలు.", "నిరోధక రకాలు; పంట మార్పిడి; అవసరమైతే Mancozeb/Azoxystrobin."),
    "corn_healthy": ("మొక్కజొన్న — ఆరోగ్యకరం", _NT, _AT),
    "grape_black_rot": ("ద్రాక్ష బ్లాక్ రాట్", "గోధుమ అంచుగల ఆకు మచ్చలు; నల్లని ఎండిన గింజలు.", "Mancozeb/Myclobutanil పిచికారీ; ఎండిన గింజలు తీసివేయండి."),
    "grape_esca": ("ద్రాక్ష ఎస్కా (బ్లాక్ మీజిల్స్)", "పులి-చారల ఆకు నమూనా; గింజలపై నల్ల మచ్చలు.", "సోకిన కలపను తీసివేయండి; కత్తిరింపు గాయాలను రక్షించండి."),
    "grape_leaf_blight": ("ద్రాక్ష ఆకు మాడు", "అక్రమ గోధుమ కోణీయ ఆకు మచ్చలు కలిసిపోతాయి.", "కాపర్ శిలీంద్రనాశిని పిచికారీ; పందిరి గాలి మెరుగుపరచండి."),
    "grape_healthy": ("ద్రాక్ష — ఆరోగ్యకరం", _NT, _AT),
    "orange_citrus_greening": ("సిట్రస్ గ్రీనింగ్ (HLB)", "మచ్చల పసుపు; వంకర చేదు పండ్లు (బాక్టీరియా, కీటకం వ్యాప్తి).", "చికిత్స లేదు — సోకిన చెట్లు తీసివేయండి; సైలిడ్ కీటకాన్ని నియంత్రించండి."),
    "peach_bacterial_spot": ("పీచ్ బాక్టీరియా మచ్చ", "చిన్న నల్ల కోణీయ ఆకు మచ్చలు; పగిలిన పండ్లు.", "కాపర్/oxytetracycline పిచికారీ; నిరోధక రకాలు."),
    "peach_healthy": ("పీచ్ — ఆరోగ్యకరం", _NT, _AT),
    "pepper_bacterial_spot": ("మిర్చి బాక్టీరియా మచ్చ", "పసుపు వలయంతో నీటిలో నానిన మచ్చలు (బాక్టీరియా).", "ధృవీకరించిన విత్తనం; కాపర్+Mancozeb పిచికారీ; పైనుండి నీరు వద్దు."),
    "pepper_healthy": ("మిర్చి — ఆరోగ్యకరం", _NT, _AT),
    "potato_early_blight": ("బంగాళదుంప ఎర్లీ బ్లైట్", "కింది ఆకులపై వలయాకార 'లక్ష్య' మచ్చలు (శిలీంధ్రం).", "Chlorothalonil/Mancozeb పిచికారీ; పైనుండి నీరు వద్దు."),
    "potato_late_blight": ("బంగాళదుంప లేట్ బ్లైట్", "తెల్ల బూజు అంచుతో నీటిలో నానిన నల్ల మచ్చలు — వేగంగా వ్యాపిస్తుంది.", "వెంటనే Cymoxanil+Mancozeb పిచికారీ; సోకిన మొక్కలు నాశనం చేయండి."),
    "potato_healthy": ("బంగాళదుంప — ఆరోగ్యకరం", _NT, _AT),
    "raspberry_healthy": ("రాస్‌బెర్రీ — ఆరోగ్యకరం", _NT, _AT),
    "soybean_healthy": ("సోయాబీన్ — ఆరోగ్యకరం", _NT, _AT),
    "squash_powdery_mildew": ("గుమ్మడి బూడిద తెగులు", "ఆకులు, కాండంపై తెల్లని బూడిద పొడి మచ్చలు.", "సల్ఫర్/potassium bicarbonate పిచికారీ; చెడ్డ ఆకులు తీసివేయండి."),
    "strawberry_leaf_scorch": ("స్ట్రాబెర్రీ ఆకు మాడు", "కలిసిపోయే అనేక చిన్న ఊదా మచ్చలు.", "మడులు పునరుద్ధరించండి; Captan పిచికారీ; గాలి, డ్రైనేజీ మెరుగుపరచండి."),
    "strawberry_healthy": ("స్ట్రాబెర్రీ — ఆరోగ్యకరం", _NT, _AT),
    "tomato_bacterial_spot": ("టమాట బాక్టీరియా మచ్చ", "పసుపు వలయంతో చిన్న నల్ల జిడ్డు మచ్చలు.", "ధృవీకరించిన విత్తనం; కాపర్+Mancozeb; పంట మార్పిడి."),
    "tomato_early_blight": ("టమాట ఎర్లీ బ్లైట్", "పాత ఆకులపై వలయాకార లక్ష్య మచ్చలు.", "Chlorothalonil/Mancozeb పిచికారీ; మల్చింగ్; కింది ఆకులు తీసివేయండి."),
    "tomato_late_blight": ("టమాట లేట్ బ్లైట్", "ఆకులు, కాండంపై నల్ల జిడ్డు మచ్చలు — వేగంగా వ్యాపిస్తుంది.", "వెంటనే Cymoxanil+Mancozeb పిచికారీ; సోకిన ఆకులు తీసివేయండి."),
    "tomato_leaf_mold": ("టమాట ఆకు బూజు", "పైన పసుపు మచ్చలు, కింద ఆలివ్-ఆకుపచ్చ బూజు.", "గాలి ప్రసరణ మెరుగుపరచండి; తేమ తగ్గించండి; Chlorothalonil పిచికారీ."),
    "tomato_septoria_spot": ("టమాట సెప్టోరియా మచ్చ", "నల్ల అంచు, బూడిద మధ్యగల అనేక చిన్న గుండ్రని మచ్చలు.", "సోకిన ఆకులు తీసివేయండి; Mancozeb పిచికారీ; ఆకులు తడపవద్దు."),
    "tomato_spider_mites": ("టమాట స్పైడర్ మైట్స్", "ఆకు అడుగున సాలెగూడుతో చుక్కలు/పసుపు.", "Abamectin లేదా సల్ఫర్ పిచికారీ; మిత్ర మైట్లను ప్రోత్సహించండి."),
    "tomato_target_spot": ("టమాట టార్గెట్ స్పాట్", "ఆకులు, పండ్లపై వలయాలతో గోధుమ మచ్చలు.", "Azoxystrobin/Chlorothalonil పిచికారీ; గాలి మెరుగుపరచండి."),
    "tomato_yellow_leaf_curl_virus": ("టమాట పసుపు ఆకు ముడత వైరస్", "పైకి ముడుచుకున్న పసుపు ఆకులు; గిడసబారిన మొక్క (వైరస్, తెల్లదోమ).", "చికిత్స లేదు — సోకిన మొక్కలు తీసివేయండి; తెల్లదోమ నియంత్రించండి."),
    "tomato_mosaic_virus": ("టమాట మొజాయిక్ వైరస్", "మచ్చల లేత/ముదురు ఆకుపచ్చ ఆకులు, వికృత పెరుగుదల (వైరస్).", "చికిత్స లేదు — సోకిన మొక్కలు తీసివేయండి; పనిముట్లు శుభ్రం చేయండి."),
    "tomato_healthy": ("టమాట — ఆరోగ్యకరం", _NT, _AT),
}


def get(key: str, lang: str = "en") -> dict:
    if key in DISEASES:
        rec = {"key": key, **DISEASES[key]}
    else:
        healthy = key.endswith("healthy")
        rec = {"key": key, "label": key.replace("_", " ").title(),
               "crop": "Unknown", "healthy": healthy, "color": _HG if healthy else _D,
               "note": "Healthy." if healthy else "Possible leaf disease detected.",
               "action": "No treatment needed." if healthy else "Consult your extension officer for diagnosis."}
    if lang == "te" and key in DISEASES_TE:
        lbl, note, act = DISEASES_TE[key]
        rec = {**rec, "label": lbl, "note": note, "action": act}
    return rec
