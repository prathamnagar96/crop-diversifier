# Google Stitch prompt — Vidarbha Crop Diversification Recommender

## ✅ CURRENT: Simple farmer-friendly version (App / mobile mode)

Stitch project: "KrishiKavach Farmer Advisory App" — https://stitch.withgoogle.com/projects/2252678007832903355
(The older detailed version below was too complex for farmers; kept for reference.)

Design a VERY SIMPLE mobile app called 'KrishiKavach' that tells farmers in Vidarbha, Maharashtra which crop to grow when a dry El Nino year (low rain) is expected. Users are small farmers with little schooling, so: one main action per screen, huge buttons, very few words, big friendly stock photos everywhere (real photos of Indian farmers, fields, cotton, soybean, tur dal, jowar, chickpea, millets, rain clouds, dry soil), simple icons, no charts, no tables, no scores, no percentages, no technical words. Language switch at top: मराठी / हिंदी / English. Only 5 screens: (1) Home: big photo of a farmer in a field, greeting 'Namaskar', one simple message card with photo of dry land 'This year less rain is expected', and one big green button 'Which crop should I grow?'. (2) Tell us about your farm: 3 simple questions shown as big photo tiles - Your district (dropdown with photo), Your soil (3 photo tiles: black soil, medium soil, light soil), Your water (3 photo tiles: only rain, well/borewell, canal). Big 'See my crops' button. (3) Best crops for you: 3 large crop cards, each with a big crop photo, crop name, one short line why (e.g. 'Needs little water'), 1-3 water drop icons for water need, a green/yellow/red dot for safety, and approximate earning in rupees per acre. Button 'Choose this crop'. (4) Crop guide: big crop photo, 'When to sow' with a simple month icon, 3 short tips with pictures, and a big 'Call helpline' button. (5) After harvest: 'Tell us how your crop did' - pick the crop you grew from photo tiles, how much you harvested (big + / - number buttons in quintals), a happy / okay / sad face to rate, and a big 'Send' button with message 'This helps us give better advice next year'. Style: warm and friendly, green and earthy colors, white background, very large readable text, lots of space.

---

## (Old) Detailed version

Paste this into https://stitch.withgoogle.com (select **Web** mode). Edit the
app name / screens to match the actual project once the repo is available.

---

Design a responsive web app called "KrishiKavach - Vidarbha Crop Diversification Advisor": an AI-powered tool that recommends climate-resilient crop mixes for farmers in El Nino-prone Vidarbha, Maharashtra (Nagpur, Amravati, Akola, Yavatmal, Wardha, Washim, Buldhana, Chandrapur, Bhandara, Gondia, Gadchiroli). Users: smallholder farmers (often on mobile, low literacy) and agriculture extension officers.

Screens:
1) Home/landing: hero with seasonal El Nino risk status (ENSO outlook badge: Neutral / Watch / El Nino likely), monsoon rainfall outlook for the selected district, big 'Get crop advice' button, language toggle English / Marathi / Hindi.
2) Farm input form (step-by-step wizard, large touch targets, icons): district and taluka, land size (acres), soil type (black cotton / medium / light), irrigation (rainfed / borewell / canal / drip), current crop (cotton, soybean, tur, etc.), budget, sowing season (Kharif / Rabi).
3) Recommendations dashboard: ranked crop-mix cards (e.g. Tur + Soybean intercrop, Jowar, Chickpea, Millets) each showing drought-resilience score, water need, expected yield and profit range, risk level chip, and 'why this crop' explanation; comparison against the current crop; rainfall vs. crop water-need chart; sowing calendar timeline.
4) Crop detail page: agronomy tips, seed varieties, input costs, nearest mandi prices, relevant government schemes (PMFBY crop insurance, PM-KISAN).
5) Officer/admin view: district map heat-map of El Nino risk and recommendation adoption.

Style: earthy and trustworthy - deep green, soil brown, warm sand and monsoon blue, clear sans-serif, high contrast, generous spacing, simple icons, mobile-first.

---

## Prompt 2 — validation + feedback screens (send after the first generation)

Add two new screens in the same KrishiKavach design system and app shell (Marathi + English): (A) 'Proven in Past El Nino Years' validation screen: district selector (default Yavatmal), a grouped bar chart comparing farmer income per acre for the KrishiKavach recommended crop mix vs the usual cotton/soybean pattern in El Nino years 2009, 2014, 2015 and 2023, a yield-loss comparison line, summary KPI cards (average income gain %, loss avoided, years where recommendation won out of 4), a methodology note 'Backtested on historical district records - model trained only on years before each season', and badges for 'Agrees with ICAR-CRIDA contingency plan' and 'Reviewed by KVK experts'. (B) 'Season Feedback' screen for after harvest: farmer reports which crops were actually planted (icon chips), area per crop, sowing date, harvest yield and income, problems faced (pests, dry spell, low price), optional crop photo upload, a comparison of reported outcome vs the app's predicted range, and a note 'Your feedback trains KrishiKavach to give better advice next season'. Use large touch targets, simple icons and the same earthy palette.

> Note: numbers Stitch puts on the validation screen are placeholders — replace with real backtest results.

## Follow-up prompts (use one at a time after the first generation)

- "Make the farm input wizard one question per screen with big icon buttons, for low-literacy users."
- "Add a Marathi version of the recommendations dashboard."
- "Add an empty/loading state and an error state for when weather data is unavailable."
- "Create a dark-mode variant of the dashboard."

## After designing

Use Stitch's export (Code → HTML/Tailwind, or Copy to Figma) and save the
export into this folder; it can then be wired to the recommender backend.
