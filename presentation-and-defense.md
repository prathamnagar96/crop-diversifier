# KrishiKavach — Presentation plan & supervisor Q&A defense

## The reframe (one sentence)

We are not claiming "farmers benefited". We claim: **"We built a risk-aware crop
recommender and validated it retrospectively on past El Niño seasons — outcomes that
are already recorded — plus crop simulation, official contingency plans and expert review.
A live field trial is Phase 2."**

## Slide flow (~12 slides)

1. Title
2. Problem — Vidarbha: rainfed, cotton/soybean-heavy, El Niño → deficit monsoon → losses (cite sources for every number)
3. Objective — district/season-specific climate-resilient crop mixes **and** a measurable evaluation of advice quality
4. Architecture — ENSO forecast + IMD rainfall + soil + irrigation → model → ranked crop mix → app → feedback loop
5. Data — ICRISAT District Level Database, DES (data.desagri.gov.in), IMD rainfall, NOAA ONI, Agmarknet prices, CACP cost of cultivation
6. Model + baselines — (a) status-quo cropping pattern, (b) ICAR-CRIDA District Contingency Plan
7. **Validation strategy** (answers the supervisors' objection directly)
   - Retrospective backtest: leave-one-El-Niño-year-out (2009, 2014, 2015, 2023)
   - Crop simulation: FAO AquaCrop for crops a district didn't grow / extreme scenarios
   - Agreement with ICAR-CRIDA contingency plans
   - Expert review: KVK / PDKV Akola scientists (agreement score)
   - Farmer usability + adoption-intent survey (SUS, TAM)
8. Results — backtest numbers (minimum: 1 district × 1 El Niño year, e.g. Yavatmal × 2015)
9. Frontend demo — Stitch screens (incl. "Proven in past El Niño years" + season feedback screen)
10. Feedback loop — farmer logs planted crop + yield → model retrains each season (demo on simulated data)
11. Limitations & Phase 2 — district-level data; market price effects; field trial with KVK
12. Timeline — deliverables this semester (none depend on a growing season)

## Likely questions & answers

**"You can't know whether the farmer will plant it."**
We evaluate *recommendation quality*, not adoption — they are separate problems. A weather
forecast is judged by accuracy, not by whether people carried umbrellas. Adoption is
addressed through design (Marathi/Hindi, low-literacy UI) and an intent survey.

**"Then how do you know the recommendation is good?"**
The outcomes already exist. In 2009/2014/2015/2023 these crops were grown in these
districts and yields were recorded. We train only on prior years, generate the
recommendation, and compare with what actually happened vs. the usual cotton/soybean pattern.

**"The past isn't the future / climate is changing."**
Leave-one-year-out including recent 2023; AquaCrop stress scenarios beyond history;
the feedback loop retrains every season.

**"District data ≠ an individual farm."**
Acknowledged limitation. Recommendations are conditioned on farm-level inputs (soil,
irrigation); simulation works at field scale; farm-level trial is Phase 2.

**"What about crops the district never grew?"**
Covered by crop simulation, ICAR-CRIDA contingency plans and expert review.

**"Where's the AI — isn't this a lookup table?"**
The model predicts yield under the forecast rainfall scenario and ranks by risk-adjusted
profit. We show it beats two baselines (status quo, contingency plan). A lookup table
can't adapt to a new forecast.

**"If everyone switches to tur, prices crash."**
Valid — we recommend a diversified mix, not one crop; market-aware diversification is future work.

**"What will you finish this semester?"**
Data pipeline, model, backtest results, frontend, feedback module, expert-review report —
none of which needs a planting season.

## Pitch line

> "We don't need to wait for future farmers — the results of growing these crops in El Niño
> years are already on record. We validate against 2009, 2014, 2015 and 2023, cross-check with
> crop simulation and ICAR-CRIDA contingency plans, and treat the field trial as Phase 2."
