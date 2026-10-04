"""Krishi Mitra — farmer chatbot for KrishiKavach.

Two modes:
  * offline (default): answers from the crop knowledge base in recommender.py,
    in Marathi / Hindi / English, using simple keyword intents. No internet,
    no API key needed.
  * ai: if the `anthropic` package is installed AND credentials are available
    (e.g. ANTHROPIC_API_KEY), questions go to Claude, grounded with the same
    knowledge base and the farmer's current profile. Falls back to offline on
    any error.
"""

import json
import os

import recommender as R

MODEL = os.environ.get("KRISHI_MODEL", "claude-opus-5-5")
HELPLINE = "1800-180-1551"

try:
    import anthropic  # optional
except ImportError:  # pragma: no cover
    anthropic = None

_client = None


def _ai_client():
    global _client
    if anthropic is None or os.environ.get("KRISHI_CHAT_OFFLINE") == "1":
        return None
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        return None
    if _client is None:
        _client = anthropic.Anthropic(max_retries=1, timeout=30.0)
    return _client


def mode():
    return "ai" if _ai_client() else "offline"


# ---------------------------------------------------------------- offline bot

CROP_WORDS = {
    "cotton": ["cotton", "kapus", "kapas", "कापूस", "कपास"],
    "soybean": ["soybean", "soyabean", "soya", "सोयाबीन"],
    "tur": ["tur", "toor", "arhar", "pigeon", "तूर", "तुर", "अरहर", "तुअर"],
    "jowar": ["jowar", "jwari", "sorghum", "ज्वारी", "ज्वार"],
    "bajra": ["bajra", "bajri", "millet", "बाजरी", "बाजरा"],
    "moong": ["moong", "mung", "mug", "green gram", "मूग", "मूंग"],
    "chickpea": ["chana", "chickpea", "gram", "harbhara", "हरभरा", "चना"],
    "safflower": ["safflower", "kardai", "karadi", "करडई", "कुसुम"],
    "wheat": ["wheat", "gahu", "gehu", "गहू", "गेहूं", "गेहूँ"],
    "paddy": ["paddy", "rice", "dhan", "bhat", "भात", "धान", "चावल"],
}

INTENT_WORDS = {
    "greet": ["hello", "hi ", "namaskar", "namaste", "ram ram", "नमस्कार", "नमस्ते", "राम राम"],
    "helpline": ["helpline", "call", "phone", "number", "हेल्पलाईन", "हेल्पलाइन", "फोन", "नंबर", "मदत", "मदद"],
    "rain": ["rain", "el nino", "elnino", "drought", "monsoon", "weather", "पाऊस", "पाउस", "बारिश", "वर्षा",
              "एल निनो", "अल नीनो", "दुष्काळ", "सूखा", "हवामान", "मौसम", "मान्सून"],
    "which": ["which crop", "what crop", "best crop", "what should i grow", "recommend", "suggest",
               "कोणते पीक", "कोणतं पीक", "कोणती पिके", "कौन सी फसल", "कौनसी फसल", "क्या बोऊं", "काय पेरू", "सल्ला"],
    "sow": ["sow", "sowing", "plant", "when", "पेरणी", "पेरू", "केव्हा", "कधी", "बुवाई", "बोना", "बोएं", "कब"],
    "harvest": ["harvest", "cut", "काढणी", "कापणी", "कटाई"],
    "water": ["water", "irrigat", "पाणी", "पानी", "सिंचाई", "ओलित"],
    "price": ["price", "rate", "msp", "earn", "income", "profit", "भाव", "दर", "कमाई", "नफा", "उत्पन्न", "मुनाफा"],
    "tips": ["how", "tip", "advice", "care", "pest", "कसे", "कसा", "कीड", "अळी", "कैसे", "कीट", "उपाय"],
}

T = {
    "greet": {
        "en": "Namaskar! I am Krishi Mitra. Ask me which crop to grow, when to sow, or how much water a crop needs.",
        "mr": "राम राम! मी कृषी मित्र. कोणते पीक घ्यावे, पेरणी कधी करावी, पाणी किती लागते — काहीही विचारा.",
        "hi": "राम राम! मैं कृषि मित्र हूं. कौन सी फसल लगाएं, बुवाई कब करें, पानी कितना लगेगा — कुछ भी पूछें.",
    },
    "helpline": {
        "en": f"Call the free Kisan Call Centre: {HELPLINE} (6 am – 10 pm). You can also visit your nearest Krishi Vigyan Kendra (KVK).",
        "mr": f"मोफत किसान कॉल सेंटर: {HELPLINE} (सकाळी ६ ते रात्री १०). जवळच्या कृषी विज्ञान केंद्रालाही भेट द्या.",
        "hi": f"मुफ़्त किसान कॉल सेंटर: {HELPLINE} (सुबह ६ से रात १०). पास के कृषि विज्ञान केंद्र से भी मिलें.",
    },
    "rain": {
        "en": "This year an El Niño is likely, so rain may be less than normal and there can be long dry gaps. Choose crops that need less water, like tur, jowar, bajra or moong, and save rain water in the field.",
        "mr": "यंदा एल निनोमुळे पाऊस सरासरीपेक्षा कमी आणि मध्ये मोठे खंड पडू शकतात. तूर, ज्वारी, बाजरी, मूग अशी कमी पाण्याची पिके घ्या आणि शेतात पावसाचे पाणी साठवा.",
        "hi": "इस साल अल नीनो से बारिश सामान्य से कम और बीच में लंबा सूखा हो सकता है. अरहर, ज्वार, बाजरा, मूंग जैसी कम पानी वाली फसलें लें और खेत में बारिश का पानी रोकें.",
    },
    "need_profile": {
        "en": "Tap 'Which crop should I grow?' and answer 4 easy questions — then I can tell you the best crops for your farm.",
        "mr": "'कोणते पीक घेऊ?' बटण दाबा आणि ४ सोपे प्रश्न सोडवा — मग तुमच्या शेतासाठी उत्तम पिके सांगतो.",
        "hi": "'कौन सी फसल लगाऊं?' बटन दबाएं और ४ आसान सवालों के जवाब दें — फिर मैं आपके खेत के लिए सबसे अच्छी फसलें बताऊंगा.",
    },
    "which": {
        "en": "For your farm, the best crops this season are: {list}. Safest: {top}.",
        "mr": "तुमच्या शेतासाठी या हंगामात उत्तम पिके: {list}. सर्वात सुरक्षित: {top}.",
        "hi": "आपके खेत के लिए इस मौसम की सबसे अच्छी फसलें: {list}. सबसे सुरक्षित: {top}.",
    },
    "sow": {
        "en": "{crop}: sow in {months}. It is ready in about {days} days.",
        "mr": "{crop}: पेरणी {months} मध्ये करा. सुमारे {days} दिवसांत तयार होते.",
        "hi": "{crop}: बुवाई {months} में करें. लगभग {days} दिन में तैयार.",
    },
    "harvest": {
        "en": "{crop}: harvest comes in {months}.",
        "mr": "{crop}: काढणी {months} मध्ये येते.",
        "hi": "{crop}: कटाई {months} में होती है.",
    },
    "water": {
        "en": "{crop} needs {level} water (about {mm} mm in the season).",
        "mr": "{crop} ला {level} पाणी लागते (हंगामात सुमारे {mm} मिमी).",
        "hi": "{crop} को {level} पानी चाहिए (मौसम में लगभग {mm} मिमी).",
    },
    "price": {
        "en": "{crop}: price is around ₹{price} per quintal (approx. government MSP). Check your local mandi rate before selling.",
        "mr": "{crop}: भाव सुमारे ₹{price} प्रति क्विंटल (अंदाजे हमीभाव). विक्रीपूर्वी जवळच्या बाजार समितीचा दर तपासा.",
        "hi": "{crop}: भाव लगभग ₹{price} प्रति क्विंटल (अनुमानित MSP). बेचने से पहले पास की मंडी का भाव देखें.",
    },
    "tips": {"en": "Tips for {crop}:", "mr": "{crop} साठी टिप्स:", "hi": "{crop} के लिए सुझाव:"},
    "crop_info": {
        "en": "{crop}: sow in {months}, ready in about {days} days, needs {level} water. Ask me about tips, water or price.",
        "mr": "{crop}: पेरणी {months}, सुमारे {days} दिवसांत तयार, {level} पाणी लागते. टिप्स, पाणी किंवा भाव विचारा.",
        "hi": "{crop}: बुवाई {months}, लगभग {days} दिन में तैयार, {level} पानी चाहिए. सुझाव, पानी या भाव पूछें.",
    },
    "unknown": {
        "en": f"Sorry, I did not understand. Try: 'When to sow tur?', 'Which crop is best?', 'Will it rain this year?'. For more help call {HELPLINE}.",
        "mr": f"माफ करा, समजले नाही. असे विचारा: 'तूर पेरणी कधी?', 'कोणते पीक चांगले?', 'यंदा पाऊस कसा?'. अधिक मदतीसाठी {HELPLINE} वर कॉल करा.",
        "hi": f"माफ़ कीजिए, समझ नहीं आया. ऐसे पूछें: 'अरहर की बुवाई कब?', 'कौन सी फसल अच्छी?', 'इस साल बारिश कैसी?'. ज़्यादा मदद के लिए {HELPLINE} पर कॉल करें.",
    },
}

LEVEL = {
    1: {"en": "little", "mr": "कमी", "hi": "कम"},
    2: {"en": "medium", "mr": "मध्यम", "hi": "मध्यम"},
    3: {"en": "a lot of", "mr": "जास्त", "hi": "ज़्यादा"},
}

MONTHS = {
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "mr": ["जानेवारी", "फेब्रुवारी", "मार्च", "एप्रिल", "मे", "जून", "जुलै", "ऑगस्ट", "सप्टेंबर", "ऑक्टोबर", "नोव्हेंबर", "डिसेंबर"],
    "hi": ["जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"],
}
AND = {"en": " – ", "mr": "–", "hi": "–"}


def _months(nums, lang):
    names = [MONTHS[lang][m - 1] for m in nums]
    return names[0] if len(names) == 1 else names[0] + AND[lang] + names[-1]


def _drops(c):
    return 1 if c["water"] < 320 else 2 if c["water"] < 600 else 3


def _find(words_map, text):
    found = []
    for key, words in words_map.items():
        if any(w in text for w in words):
            found.append(key)
    return found


def offline_reply(message, lang, profile):
    text = " " + message.lower() + " "
    crops = _find(CROP_WORDS, text)
    intents = _find(INTENT_WORDS, text)
    crop_id = crops[0] if crops else None

    if crop_id:
        c = R.CROPS[crop_id]
        name = c["name"][lang]
        fmt = {"crop": name, "months": _months(c["sow"], lang), "days": c["days"],
               "level": LEVEL[_drops(c)][lang], "mm": c["water"], "price": f"{c['price']:,}"}
        if "harvest" in intents:
            return T["harvest"][lang].format(crop=name, months=_months(c["harvest"], lang))
        if "price" in intents:
            return T["price"][lang].format(**fmt)
        if "water" in intents:
            return T["water"][lang].format(**fmt)
        if "tips" in intents:
            tips = "\n".join(f"• {t[lang]}" for t in c["tips"])
            return T["tips"][lang].format(crop=name) + "\n" + tips
        if "sow" in intents:
            return T["sow"][lang].format(**fmt)
        return T["crop_info"][lang].format(**fmt)

    if "which" in intents:
        if not profile or not all(profile.get(k) for k in ("district", "soil", "water", "season")):
            return T["need_profile"][lang]
        res = R.recommend(profile["district"], profile["soil"], profile["water"], profile["season"])
        names = [R.CROPS[r["id"]]["name"][lang] for r in res["crops"]]
        return T["which"][lang].format(list=", ".join(names), top=names[0])
    if "rain" in intents:
        return T["rain"][lang]
    if "helpline" in intents:
        return T["helpline"][lang]
    if "greet" in intents:
        return T["greet"][lang]
    return T["unknown"][lang]


# --------------------------------------------------------------------- AI bot

LANG_NAME = {"en": "simple English", "mr": "simple Marathi (मराठी)", "hi": "simple Hindi (हिंदी)"}

SYSTEM = """You are Krishi Mitra, the helper inside KrishiKavach, an app that advises small farmers in Vidarbha, Maharashtra which crops to grow in a likely El Niño (low-rain) year.

How to answer:
- Many users have little schooling. Use short, warm, everyday words. 2–4 short sentences, or up to 3 bullet points. No jargon, no tables.
- Base crop facts on the KNOWLEDGE BASE below (approximate demo values). If something is not covered, give general, safe farming advice and suggest the Kisan Call Centre 1800-180-1551 or the nearest Krishi Vigyan Kendra (KVK).
- Never invent exact prices, subsidies or scheme amounts. Say prices are approximate and to check the local mandi.
- For pesticide or chemical doses, do not give quantities — tell them to ask the KVK or an agriculture officer.
- If the question is not about farming, politely bring it back to farming.

KNOWLEDGE BASE (JSON):
"""


def _kb():
    crops = {cid: {k: v for k, v in c.items() if k != "tips"} | {"tips": [t["en"] for t in c["tips"]]}
             for cid, c in R.CROPS.items()}
    return json.dumps({"outlook": R.OUTLOOK, "districts": R.DISTRICTS, "crops": crops},
                      ensure_ascii=False, sort_keys=True)


_SYSTEM_BLOCK = None


def ai_reply(message, lang, profile, history):
    global _SYSTEM_BLOCK
    client = _ai_client()
    if _SYSTEM_BLOCK is None:
        # Stable, cacheable prefix: instructions + knowledge base.
        _SYSTEM_BLOCK = [{"type": "text", "text": SYSTEM + _kb(), "cache_control": {"type": "ephemeral"}}]

    context = f"Reply in {LANG_NAME.get(lang, 'simple English')}."
    if profile and all(profile.get(k) for k in ("district", "soil", "water", "season")):
        rec = R.recommend(profile["district"], profile["soil"], profile["water"], profile["season"])
        context += (f" Farmer's farm: district={profile['district']}, soil={profile['soil']}, "
                    f"water={profile['water']}, season={profile['season']}. "
                    f"App's current top crops for them: {[r['id'] for r in rec['crops']]}.")

    messages = []
    for h in (history or [])[-8:]:
        if h.get("role") in ("user", "assistant") and h.get("text"):
            messages.append({"role": h["role"], "content": h["text"][:1000]})
    if messages and messages[0]["role"] != "user":
        messages = messages[1:]
    messages.append({"role": "user", "content": f"{context}\n\nQuestion: {message[:1000]}"})

    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=2000,
        output_config={"effort": "low"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        system=_SYSTEM_BLOCK,
        messages=messages,
    )
    if response.stop_reason == "refusal":
        return None
    text = "".join(b.text for b in response.content if b.type == "text").strip()
    return text or None


def reply(message, lang="mr", profile=None, history=None):
    lang = lang if lang in ("en", "mr", "hi") else "mr"
    message = (message or "").strip()
    if not message:
        return {"reply": T["greet"][lang], "mode": mode()}
    if _ai_client():
        try:
            text = ai_reply(message, lang, profile, history)
            if text:
                return {"reply": text, "mode": "ai"}
        except Exception as e:  # network / auth / API errors -> offline answer
            print(f"[chat] AI mode failed, using offline answer: {type(e).__name__}: {e}")
    return {"reply": offline_reply(message, lang, profile), "mode": "offline"}
