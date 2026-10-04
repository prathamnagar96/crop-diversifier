"""KrishiKavach crop recommender — explainable rule-based scoring.

This is a transparent baseline model: every recommendation can be traced to
soil fit, water balance under the El Nino rain outlook, and drought tolerance.
It is meant to be replaced/augmented by the ML model trained on historical
district data (ICRISAT / DES / IMD) and validated by the El Nino backtest.

All agronomic and price numbers are APPROXIMATE demo values (prices are close
to recent MSP levels) and must be replaced with sourced data before real use.
"""

# --- Season outlook (demo) ---------------------------------------------------
# In the full system this comes from the IMD / NOAA ENSO forecast.
OUTLOOK = {
    "status": "el_nino_likely",   # neutral | el_nino_watch | el_nino_likely
    "rain_change": -0.15,          # expected change vs normal monsoon rain
}

# --- Districts of Vidarbha ---------------------------------------------------
# normal_rain: approximate long-period average annual rainfall (mm).
DISTRICTS = {
    "buldhana":   {"en": "Buldhana",   "mr": "बुलढाणा",   "hi": "बुलढाणा",   "normal_rain": 760},
    "akola":      {"en": "Akola",      "mr": "अकोला",     "hi": "अकोला",     "normal_rain": 800},
    "washim":     {"en": "Washim",     "mr": "वाशिम",     "hi": "वाशिम",     "normal_rain": 880},
    "amravati":   {"en": "Amravati",   "mr": "अमरावती",   "hi": "अमरावती",   "normal_rain": 850},
    "yavatmal":   {"en": "Yavatmal",   "mr": "यवतमाळ",    "hi": "यवतमाल",    "normal_rain": 920},
    "wardha":     {"en": "Wardha",     "mr": "वर्धा",      "hi": "वर्धा",      "normal_rain": 1000},
    "nagpur":     {"en": "Nagpur",     "mr": "नागपूर",     "hi": "नागपुर",     "normal_rain": 1050},
    "chandrapur": {"en": "Chandrapur", "mr": "चंद्रपूर",    "hi": "चंद्रपुर",    "normal_rain": 1250},
    "bhandara":   {"en": "Bhandara",   "mr": "भंडारा",    "hi": "भंडारा",    "normal_rain": 1300},
    "gondia":     {"en": "Gondia",     "mr": "गोंदिया",    "hi": "गोंदिया",    "normal_rain": 1400},
    "gadchiroli": {"en": "Gadchiroli", "mr": "गडचिरोली",  "hi": "गढ़चिरौली",  "normal_rain": 1450},
}

# --- Crops -------------------------------------------------------------------
# water: seasonal water need (mm); tol: drought tolerance 0..1; days: duration
# soil: suitability per soil type 0..1; yield: normal q/acre (low, high)
# price: Rs/quintal (approx. MSP); cost: Rs/acre; irrigated: needs assured water
# sow / harvest: month numbers
CROPS = {
    "tur": {
        "name": {"en": "Tur (Pigeon pea)", "mr": "तूर", "hi": "अरहर (तुअर)"},
        "season": "kharif", "water": 400, "tol": 0.85, "days": 165,
        "soil": {"black": 1.0, "medium": 0.9, "light": 0.6},
        "yield": (3, 6), "price": 7550, "cost": 12000, "irrigated": False,
        "sow": [6, 7], "harvest": [12, 1],
        "tips": [
            {"en": "Sow only after 75–100 mm of rain has fallen.",
             "mr": "७५–१०० मिमी पाऊस झाल्यावरच पेरणी करा.",
             "hi": "७५–१०० मिमी बारिश होने के बाद ही बुवाई करें."},
            {"en": "Grow with soybean: 4 rows soybean, 2 rows tur.",
             "mr": "सोयाबीनसोबत ४:२ ओळीत आंतरपीक घ्या.",
             "hi": "सोयाबीन के साथ ४:२ कतार में अंतरफसल लें."},
            {"en": "At flowering, put pheromone traps for pod borer.",
             "mr": "फुलोऱ्यात शेंगा पोखरणाऱ्या अळीसाठी कामगंध सापळे लावा.",
             "hi": "फूल आने पर फली छेदक के लिए फेरोमोन ट्रैप लगाएं."},
        ],
    },
    "soy_tur": {
        "name": {"en": "Soybean + Tur", "mr": "सोयाबीन + तूर", "hi": "सोयाबीन + अरहर"},
        "season": "kharif", "water": 430, "tol": 0.7, "days": 165,
        "soil": {"black": 1.0, "medium": 0.9, "light": 0.5},
        "yield": (5, 8), "price": 6200, "cost": 14000, "irrigated": False,
        "sow": [6, 7], "harvest": [10, 1], "intercrop": True,
        "tips": [
            {"en": "Sow 4 rows of soybean, then 2 rows of tur.",
             "mr": "४ ओळी सोयाबीन, नंतर २ ओळी तूर पेरा.",
             "hi": "४ कतार सोयाबीन, फिर २ कतार अरहर बोएं."},
            {"en": "If rain stops early, tur still survives and pays.",
             "mr": "पाऊस लवकर गेला तरी तूर टिकते आणि पैसे देते.",
             "hi": "बारिश जल्दी रुके तो भी अरहर बचती है और कमाई देती है."},
            {"en": "Cut soybean in October, tur in January.",
             "mr": "सोयाबीन ऑक्टोबरमध्ये, तूर जानेवारीत काढा.",
             "hi": "सोयाबीन अक्टूबर में, अरहर जनवरी में काटें."},
        ],
    },
    "jowar": {
        "name": {"en": "Jowar", "mr": "ज्वारी", "hi": "ज्वार"},
        "season": "kharif", "water": 350, "tol": 0.8, "days": 110,
        "soil": {"black": 0.9, "medium": 1.0, "light": 0.7},
        "yield": (6, 10), "price": 3370, "cost": 10000, "irrigated": False,
        "sow": [6, 7], "harvest": [10],
        "tips": [
            {"en": "Choose a short-duration hybrid seed.",
             "mr": "कमी कालावधीचे संकरित बियाणे निवडा.",
             "hi": "कम अवधि वाला संकर बीज चुनें."},
            {"en": "You get grain for home and fodder for cattle.",
             "mr": "घरासाठी धान्य आणि जनावरांसाठी कडबा मिळतो.",
             "hi": "घर के लिए अनाज और पशुओं के लिए चारा मिलता है."},
            {"en": "Thin out extra plants 15 days after sowing.",
             "mr": "पेरणीनंतर १५ दिवसांनी विरळणी करा.",
             "hi": "बुवाई के १५ दिन बाद घने पौधे निकालें."},
        ],
    },
    "bajra": {
        "name": {"en": "Bajra", "mr": "बाजरी", "hi": "बाजरा"},
        "season": "kharif", "water": 300, "tol": 0.9, "days": 85,
        "soil": {"black": 0.6, "medium": 0.9, "light": 1.0},
        "yield": (5, 8), "price": 2625, "cost": 8000, "irrigated": False,
        "sow": [7], "harvest": [9, 10],
        "tips": [
            {"en": "Best crop for light, sandy soil.",
             "mr": "हलक्या, वाळूमिश्रित जमिनीसाठी उत्तम पीक.",
             "hi": "हल्की, रेतीली मिट्टी के लिए सबसे अच्छी फसल."},
            {"en": "Ready in about 85 days.",
             "mr": "सुमारे ८५ दिवसांत तयार होते.",
             "hi": "लगभग ८५ दिन में तैयार."},
            {"en": "Give a small dose of fertilizer at sowing.",
             "mr": "पेरणीच्या वेळी थोडे खत द्या.",
             "hi": "बुवाई के समय थोड़ी खाद दें."},
        ],
    },
    "moong": {
        "name": {"en": "Moong", "mr": "मूग", "hi": "मूंग"},
        "season": "kharif", "water": 250, "tol": 0.6, "days": 65,
        "soil": {"black": 0.9, "medium": 1.0, "light": 0.8},
        "yield": (2, 4), "price": 8680, "cost": 8000, "irrigated": False,
        "sow": [6, 7], "harvest": [9],
        "tips": [
            {"en": "Ready in 60–65 days, before the rain stops.",
             "mr": "६०–६५ दिवसांत तयार, पाऊस जाण्याआधी.",
             "hi": "६०–६५ दिन में तैयार, बारिश रुकने से पहले."},
            {"en": "Can be sown till mid-July if rain is late.",
             "mr": "पाऊस उशिरा आला तरी जुलै मध्यापर्यंत पेरता येते.",
             "hi": "बारिश देर से आए तो जुलाई मध्य तक बो सकते हैं."},
            {"en": "After harvest, grow chana on the same field.",
             "mr": "काढणीनंतर त्याच शेतात हरभरा घ्या.",
             "hi": "कटाई के बाद उसी खेत में चना लें."},
        ],
    },
    "soybean": {
        "name": {"en": "Soybean", "mr": "सोयाबीन", "hi": "सोयाबीन"},
        "season": "kharif", "water": 450, "tol": 0.35, "days": 100,
        "soil": {"black": 1.0, "medium": 0.8, "light": 0.4},
        "yield": (4, 7), "price": 4890, "cost": 15000, "irrigated": False,
        "sow": [6, 7], "harvest": [9, 10],
        "tips": [
            {"en": "Sow only after 75–100 mm of rain.",
             "mr": "७५–१०० मिमी पाऊस झाल्यावरच पेरा.",
             "hi": "७५–१०० मिमी बारिश के बाद ही बोएं."},
            {"en": "Use raised beds with furrows to save rain water.",
             "mr": "रुंद वरंबा-सरी पद्धतीने पेरा, पावसाचे पाणी साठते.",
             "hi": "मेड़-नाली विधि से बोएं, बारिश का पानी बचता है."},
            {"en": "Treat seed with Rhizobium before sowing.",
             "mr": "पेरणीपूर्वी बियाण्याला रायझोबियम लावा.",
             "hi": "बुवाई से पहले बीज पर राइजोबियम लगाएं."},
        ],
    },
    "cotton": {
        "name": {"en": "Cotton", "mr": "कापूस", "hi": "कपास"},
        "season": "kharif", "water": 700, "tol": 0.35, "days": 170,
        "soil": {"black": 1.0, "medium": 0.7, "light": 0.3},
        "yield": (4, 8), "price": 7120, "cost": 20000, "irrigated": False,
        "sow": [6, 7], "harvest": [11, 12, 1],
        "tips": [
            {"en": "In a dry year, grow cotton only if you have well water.",
             "mr": "कोरड्या वर्षी विहिरीचे पाणी असेल तरच कापूस घ्या.",
             "hi": "सूखे साल में कुएं का पानी हो तभी कपास लें."},
            {"en": "Put pheromone traps for pink bollworm.",
             "mr": "गुलाबी बोंडअळीसाठी कामगंध सापळे लावा.",
             "hi": "गुलाबी सुंडी के लिए फेरोमोन ट्रैप लगाएं."},
            {"en": "Cover soil between rows to keep moisture.",
             "mr": "ओळींमध्ये आच्छादन करा, ओलावा टिकतो.",
             "hi": "कतारों के बीच मल्च बिछाएं, नमी बनी रहती है."},
        ],
    },
    "paddy": {
        "name": {"en": "Paddy (Rice)", "mr": "भात", "hi": "धान"},
        "season": "kharif", "water": 1100, "tol": 0.1, "days": 120,
        "soil": {"black": 0.8, "medium": 1.0, "light": 0.4},
        "yield": (15, 22), "price": 2300, "cost": 25000, "irrigated": True,
        "sow": [6, 7], "harvest": [10, 11],
        "tips": [
            {"en": "Grow only with canal or assured water.",
             "mr": "कालवा किंवा खात्रीचे पाणी असेल तरच घ्या.",
             "hi": "नहर या पक्का पानी हो तभी लें."},
            {"en": "Transplant 21–25 day old seedlings.",
             "mr": "२१–२५ दिवसांची रोपे लावा.",
             "hi": "२१–२५ दिन की पौध रोपें."},
            {"en": "Keep 2–5 cm water standing in the field.",
             "mr": "शेतात २–५ सेमी पाणी साठवून ठेवा.",
             "hi": "खेत में २–५ सेमी पानी भरा रखें."},
        ],
    },
    "chickpea": {
        "name": {"en": "Chana (Gram)", "mr": "हरभरा", "hi": "चना"},
        "season": "rabi", "water": 250, "tol": 0.75, "days": 105,
        "soil": {"black": 1.0, "medium": 0.8, "light": 0.4},
        "yield": (4, 7), "price": 5650, "cost": 12000, "irrigated": False,
        "sow": [10, 11], "harvest": [2, 3],
        "tips": [
            {"en": "Sow in black soil using the moisture left after rains.",
             "mr": "पावसानंतर काळ्या जमिनीतील ओलाव्यावर पेरणी करा.",
             "hi": "बारिश के बाद काली मिट्टी की नमी में बोएं."},
            {"en": "One light watering at flowering gives more grain.",
             "mr": "फुलोऱ्यात एक हलके पाणी दिल्यास उत्पादन वाढते.",
             "hi": "फूल आने पर एक हल्की सिंचाई से पैदावार बढ़ती है."},
            {"en": "Put bird perches in the field — birds eat the worms.",
             "mr": "शेतात पक्षी थांबे लावा, पक्षी अळ्या खातात.",
             "hi": "खेत में पक्षी बैठने के डंडे लगाएं, पक्षी इल्लियां खाते हैं."},
        ],
    },
    "safflower": {
        "name": {"en": "Safflower", "mr": "करडई", "hi": "कुसुम"},
        "season": "rabi", "water": 200, "tol": 0.9, "days": 125,
        "soil": {"black": 1.0, "medium": 0.8, "light": 0.5},
        "yield": (3, 5), "price": 5940, "cost": 8000, "irrigated": False,
        "sow": [9, 10], "harvest": [2],
        "tips": [
            {"en": "Deep roots — needs very little water.",
             "mr": "खोल मुळे — खूप कमी पाणी लागते.",
             "hi": "गहरी जड़ें — बहुत कम पानी चाहिए."},
            {"en": "Thorny plant, so animals don't eat it.",
             "mr": "काटेरी असल्याने जनावरे खात नाहीत.",
             "hi": "कांटेदार पौधा, पशु नहीं खाते."},
            {"en": "Sow in Sept–Oct on stored soil moisture.",
             "mr": "सप्टेंबर–ऑक्टोबरमध्ये जमिनीतील ओलाव्यावर पेरा.",
             "hi": "सितंबर–अक्टूबर में मिट्टी की नमी पर बोएं."},
        ],
    },
    "wheat": {
        "name": {"en": "Wheat", "mr": "गहू", "hi": "गेहूं"},
        "season": "rabi", "water": 450, "tol": 0.2, "days": 120,
        "soil": {"black": 1.0, "medium": 0.9, "light": 0.5},
        "yield": (12, 18), "price": 2425, "cost": 18000, "irrigated": True,
        "sow": [11], "harvest": [3],
        "tips": [
            {"en": "Needs 4–5 waterings — only if water is assured.",
             "mr": "४–५ पाणी लागते — पाणी खात्रीचे असेल तरच.",
             "hi": "४–५ सिंचाई चाहिए — पानी पक्का हो तभी."},
            {"en": "Sow in the first half of November.",
             "mr": "नोव्हेंबरच्या पहिल्या पंधरवड्यात पेरा.",
             "hi": "नवंबर के पहले पखवाड़े में बोएं."},
            {"en": "Most important watering: 21 days after sowing.",
             "mr": "सर्वात महत्त्वाचे पाणी: पेरणीनंतर २१ दिवसांनी.",
             "hi": "सबसे ज़रूरी सिंचाई: बुवाई के २१ दिन बाद."},
        ],
    },
}

# Usual crop farmers grow, used for the "this year it is risky" comparison.
USUAL_CROP = {"kharif": "cotton", "rabi": "wheat"}

# Extra water (mm) a source can add over a season.
WATER_BONUS = {"rain": 0, "well": 180, "canal": 450}
# Moisture stored in soil after the monsoon (rabi crops live on this).
RESIDUAL_MOISTURE = {"black": 220, "medium": 130, "light": 60}


def _water_supply(district, soil, water, season):
    normal = DISTRICTS[district]["normal_rain"]
    expected = normal * (1 + OUTLOOK["rain_change"])
    if season == "kharif":
        # roughly 85% of annual rain falls June–September; a crop can use ~55% of it
        base = expected * 0.85 * 0.55
    else:
        base = RESIDUAL_MOISTURE[soil]
    return base + WATER_BONUS[water]


def _round500(x):
    return int(round(x / 500.0)) * 500


def evaluate(crop_id, district, soil, water, season):
    c = CROPS[crop_id]
    supply = _water_supply(district, soil, water, season)
    ratio = min(1.2, supply / c["water"])
    # Yield factor: tolerant crops lose less when water is short.
    short = max(0.0, 1.0 - ratio)
    factor = max(0.15, 1.0 - short * (1.6 - 1.2 * c["tol"]))
    soil_fit = c["soil"][soil]
    factor *= 0.6 + 0.4 * soil_fit

    lo, hi = c["yield"]
    net_lo = lo * factor * c["price"] - c["cost"]
    net_hi = hi * factor * c["price"] - c["cost"]

    if factor >= 0.8:
        safety = "safe"
    elif factor >= 0.6:
        safety = "medium"
    else:
        safety = "risky"

    drops = 1 if c["water"] < 320 else 2 if c["water"] < 600 else 3

    reasons = []
    if c.get("intercrop"):
        reasons.append({"code": "intercrop_safety"})
    if drops == 1:
        reasons.append({"code": "low_water"})
    if c["tol"] >= 0.75:
        reasons.append({"code": "drought_hardy"})
    if c["days"] <= 90:
        reasons.append({"code": "short_duration", "days": c["days"]})
    if season == "rabi" and soil == "black" and not c["irrigated"]:
        reasons.append({"code": "uses_moisture"})
    if soil_fit >= 0.9:
        reasons.append({"code": "suits_soil"})
    if c["price"] >= 7000:
        reasons.append({"code": "good_price"})
    if ratio >= 1.0 and water != "rain":
        reasons.append({"code": "water_ok"})

    # Overall score: expected outcome, weighted toward safety in an El Nino year.
    mid_income = (net_lo + net_hi) / 2
    score = 0.45 * factor + 0.25 * soil_fit + 0.15 * c["tol"] + 0.15 * max(0, min(1, mid_income / 40000))

    return {
        "id": crop_id,
        "score": round(score, 3),
        "safety": safety,
        "drops": drops,
        "days": c["days"],
        "earning": [_round500(max(net_lo, -c["cost"])), _round500(max(net_hi, 0))],
        "reasons": reasons[:2],
        "sow": c["sow"],
        "harvest": c["harvest"],
    }


def recommend(district, soil, water, season, top=3):
    if district not in DISTRICTS:
        raise ValueError("unknown district")
    if soil not in RESIDUAL_MOISTURE or water not in WATER_BONUS or season not in ("kharif", "rabi"):
        raise ValueError("bad input")

    results = []
    for cid, c in CROPS.items():
        if c["season"] != season:
            continue
        if c["irrigated"] and water == "rain":
            continue
        results.append(evaluate(cid, district, soil, water, season))
    results.sort(key=lambda r: r["score"], reverse=True)

    usual_id = USUAL_CROP[season]
    usual = evaluate(usual_id, district, soil, water, season)
    return {
        "outlook": OUTLOOK,
        "crops": results[:top],
        "usual": {"id": usual_id, "safety": usual["safety"]},
    }
