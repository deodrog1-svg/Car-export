# Professional Car Broker: exact delivered price to any country and city

Viral Max is also a **professional car import broker**. The user sends car details and a destination
country and city. Viral Max returns an **exact, itemized price quote as a PDF in Russian**.

## Tools

| File | What it is |
|---|---|
| `viral-max/tools/landed_cost.py` | The calculator. `python3 viral-max/tools/landed_cost.py <request.json>` writes `viral-max/quotes/NNN-*.md` + `.pdf` |
| `viral-max/tools/costs.json` | The user's own costs (Korea fees, service fee, insurance %, **exchange rates**) |
| `viral-max/tools/countries/<country>.json` | One customs and logistics profile per country (rules, freight, cities, documents, sources) |
| `viral-max/tools/countries/_template.json` | Schema and help for building a new country profile |
| `viral-max/quotes/` | Request JSONs and finished quotes |

## Compare mode (several countries at once, video captions)

Put `"destinations": [{"country": ..., "city": ...}, ...]` in the request instead of country/city. The calculator
writes one comparison PDF (summary table + itemized breakdown per country) and prints a **ready caption block**.
If one country can't be calculated (e.g. Russia >160 hp or >2000 cc), it shows ❌ with the reason and the others still run.
Default caption countries: Kazakhstan (Алматы), Kyrgyzstan (Бишкек), Georgia (Тбилиси), Russia (Владивосток). Command: `/caption`.

**Profiles available:** `kazakhstan`, `kyrgyzstan`, `georgia`, `russia` (built 2026-10-26 from open sources; each item marked
`check`: `official` / `sources` (2+ open sources agree) / `estimate` ⚠️). Uzbekistan is not built yet: sources contradict each other
(duty 15% vs 40% + $3/cc), so research it properly before adding.

**Key Kazakhstan rules (corrected 2026-10-26 with the brokers' table from the owner):**
- Private imports are cleared with the **EAEU single rate (ЕТС, EEC Council Decision 107, annex 2)**. It replaces duty, VAT and excise.
  Under 3 years: 48–54% of value but at least 2.5–20 €/cc (depending on value). **3–5 years: only per cc** (1.5–3.6 €/cc; 2.7 for 1.8–2.3 L).
  Over 5 years: personal import is not allowed since 28.09.2026 (legal entity only).
- So **3–5-year-old cars are usually the cheapest to import**, especially expensive (German) cars, even with the 500 MRP (≈2.16M ₸)
  first registration fee that applies after 3 years (2–3 years: 50 MRP).
- Profile `kazakhstan` = ЕТС (default). `kazakhstan-dt` = legal-entity alternative (ETT duty + 16% VAT). The quote shows the alternative total
  for comparison, which is sometimes cheaper for expensive cars under 3 years.
- Plus: utilsbor (jumps above 2000 cc), customs fee 6 MRP, plates. Always compare with Kolesa.kz prices.
- **Cheapest legal route is chosen automatically:** for Kazakhstan and Kyrgyzstan the calculator runs both the private-import ETS and the
  legal-entity route (`*-dt` profiles), quotes the cheaper one, and shows the other for comparison. If private import is not allowed
  (Kazakhstan: car older than 5 years), it switches to the legal-entity route and the caption says "через юрлицо".
- Legal-entity duty for cars older than 7 years: 1.4–3.2 €/cc by engine size (range from sputnik.kg; the per-bracket split is an estimate, so confirm with a broker).

## Workflow for every price request

1. **Collect the car data.** You need model and trim, year (plus month if known), fuel type, engine cc,
   horsepower (Russia/EAEU and some others tax by hp; EVs need motor kW), mileage, price in KRW
   (or the listing link), destination country and city, and container or RoRo.
   If something essential is missing, ask once for everything missing in a single message. If the user sends
   a listing link (Encar, KCar...), read it to get the data.
2. **Update exchange rates** in `costs.json` (`fx`, `fx_date`) from a current source (central bank
   or a major FX site) if they are older than 1 day.
3. **Check the country profile** `countries/<country>.json`:
   - **Missing or `verified_on` older than 30 days?** Research and rebuild it (see below).
   - City missing? Research inland transport cost and time from the port or border to that city and add it.
4. **Write the request** as `viral-max/quotes/<NNN>-request-<slug>.json` and run the calculator.
5. **Sanity check.** Compare the total against real local listings for the same car (local car
   sites). If the gap is suspicious, re-check the rules. Mention the comparison in your reply: it is
   the strongest selling argument.
6. **Send the PDF** with a 3–4 line summary in Russian: total in USD and local currency, the biggest
   cost items, and what is still ⚠️ unconfirmed.

## How to research a country (be a real broker)

Research in this order and **always save the source URL** in the item's `source` and in `sources`:

1. **Official customs/tax authority** of the country (customs service, tax code, government decrees,
   official customs calculators). This is the only source that gives `verified: true`.
2. Regional union rules: **EAEU** (Russia, Kazakhstan, Kyrgyzstan, Armenia, Belarus) shares a Unified
   Customs Tariff, but VAT, excise, recycling fees and certification differ per country. Look for
   "ЕТТ ЕАЭС легковые автомобили ставки" and each country's own fees.
3. Local customs-broker calculators and recent news (only to cross-check; `verified: false`).

Things that are often forgotten. Always check them:
- Duty that depends on **age** (0–3, 3–5, 5–7, 7+ years) and **engine size or horsepower**
- "Whichever is higher" rules (% of value vs. €/cc) → use `max`
- **Excise** (by cc or hp), **VAT** base (usually CIF + duty + excise), **recycling fee** (утильсбор),
  customs processing fee, **certification** (СБКТС/ЭПТС, homologation), registration and plates,
  mandatory insurance, transit fees through third countries
- **EV/hybrid exemptions** and their expiry dates
- **Bans and limits**: maximum age, right-hand-drive bans, Korean export restrictions (e.g. Russia)
- The route: by sea straight to a port, or by sea plus rail or truck through a third country
  (e.g. Central Asia often goes via Vladivostok, China or Georgia/Poti). Freight comes from the
  user's real quotes in `teach/lessons.md` if available. Otherwise use a researched estimate with
  `freight_verified: false`.

## Honesty rules

- **"Exact" means every number is traceable.** Never invent a rate. If a number can't be confirmed,
  mark it `verified: false`. The PDF then flags it ⚠️ and says it needs confirmation.
- Customs makes the final calculation on the day of clearance. The quote says so.
- Quotes are valid for 7 days (`quote_valid_days`) because exchange rates and rules move.
- When the user teaches real costs (freight, broker fees per country), put them into the profile and
  `costs.json` and set `verified: true` for those items (source: "данные компании").

## Calibration log

- **2026-11-02, Kazakhstan (Almaty):** checked against a competitor's itemized turnkey card (youcar.kz, Carnival 2022 2.2D,
  $20 363 in Korea → 18 690 000 ₸). Our calculator gives 17 483 208 ₸ (−6%). ETS, recycling fee and the 500 MRP registration
  match to the tenge. The whole gap is in the estimated items: freight ($2 500 sedan/SUV, $4 000 minivan at youcar vs our $2 800)
  and local services (≈$1 600: broker, SBKTS + GLONASS, temporary storage, EPTS etc. vs our 45 000 ₸). Until the user teaches real
  costs, tell clients the local-services line is an estimate and may be ≈$1 500 higher. Details: `countries/kazakhstan.json`
  → `_calibration_2026_11_02`.
- **2026-11-02, Russia:** recycling fee indexation +10–20% from 01.01.2027 (decree №1255). Personal-use rate ≤160 hp stays.
  Re-check commercial rates in `countries/russia.json` after 01.01.2027.
- **2026-11-03, Kazakhstan (upcoming, draft):** the 2027–2029 budget bill proposes MRP = 4 693 ₸ from 01.01.2027 (now 4 325 ₸, +8.5%).
  Every MRP-based line grows: registration >3 yrs 500 MRP = 2 346 500 ₸ (+184 000), ≤3 yrs 50 MRP = 234 650 ₸; recycling fee
  1.0–2.0 L 821 275 ₸, 2.0–3.0 L 1 173 250 ₸, >3 L 2 698 475 ₸; customs fee 6 MRP ≈ 28 158 ₸ (kolesa.kz, 01.09.2026). Not law yet:
  do NOT change `countries/kazakhstan.json` amounts until the budget law is signed; for cars cleared after 01.01.2027 warn the client
  (≈+280 000 ₸ on a 2.2 L car older than 3 years). Note stored in `countries/kazakhstan.json` → `_upcoming_2027`.
- **2026-11-04, Kazakhstan EVs (resolves the 03.11 [VERIFY] contradiction):** the EEC duty-free EV quota ended 01.01.2026 (that part
  of our data was right). prigon.kz/kolesa.kz were also right in a narrower sense: under Kazakhstan's WTO exemption list an individual
  can clear an EV at **0% duty + 16% VAT**, but the car may not be sold or transferred to other EAEU states. The default EAEU route is
  **15% duty + 16% VAT ≈ 31%** (what the calculator uses). EVs pay no recycling fee, and first registration of a used EV is **half**
  the ICE rate (≈1 081 250 ₸ for EVs over 3 years, 108 125 ₸ for 2–3 years) — now built into `countries/kazakhstan.json`
  (finance.kz updated 03.11.2026; kolesa.kz 11.09.2025). Quote both regimes to EV clients and confirm the WTO regime with the broker
  **[VERIFY]**. Test (scratch): Niro EV 2022 ₩22M → Almaty $28 655 (registration $2 397 instead of $4 794).
- **2026-11-13, Kazakhstan registration fee (no rule change, [VERIFY]):** kolesa.kz's 2026 table (24.12.2025, updated 10.09.2026)
  labels the age bands by **year of manufacture**: in 2026, 2025–2026 cars pay 0.25 MRP, **2024 cars 50 MRP**, 2023 and older 500 MRP;
  the EV half rate (25/250 MRP) explicitly **excludes hybrids**. youcar.kz cards (11–12.11) differ in two ways: hybrids get the EV rate
  (Tucson HEV 2025 → 108 125 ₸, Tucson/Carnival HEV 2023–2024 → 1 081 250 ₸) and the bands look shifted by one year (diesel 2024 → 500 MRP),
  as if registration happened in 2027. Our profile follows kolesa.kz on hybrids. **Known gap:** `landed_cost.py` measures age in days from
  the manufacture month, not by calendar year, so a 2024/12 car gets 1 081 ₸ (table: 216 250 ₸) and a 2023/12 car gets 216 250 ₸
  (table: 2 162 500 ₸). Not changed: the official Tax Code text (НК РК № 214-VIII) was not readable on adilet. Since 12.10.2026 the fee is
  paid before customs release, so the release date decides the band. For 2023–2024 cars, tell the client the registration line may jump
  to 500 MRP if release slips into 2027, and confirm with the broker.
- **2026-11-14, Kazakhstan registration fee: calendar-year counting is backed by an official KGD answer ([VERIFY] for the new code text):**
  the KGD chairman's answer of 27.12.2021 (prg.kz doc 37683384, old Tax Code art. 553 p. 4) writes every band as
  "до 2 лет, **включая год выпуска**" (0.25 MRP), "от 2 до 3 лет, включая год выпуска" (50 MRP), "от 3 лет и выше" (500 MRP);
  EVs "за исключением гибридных" 0.25/25/250 MRP. calk.kz (updated 04.11.2026) cites the new code as **art. 615 p. 3, lines 4.1–4.4**
  and computes age = current calendar year − model year. So the band is set by **(year of registration − year of manufacture)**:
  in 2026 → 2025–2026 cars 0.25 MRP, 2024 cars 50 MRP, ≤2023 cars 500 MRP; on 01.01.2027 every car moves up one band.
  The day/month count in `landed_cost.py` is the outlier (2024/12 → 0.25 MRP instead of 50; 2023/12 → 50 instead of 500).
  **Code not changed — owner decision pending.** youcar.kz cards of 13.11 charge 500 MRP to 2024 cars (G80 2024, K3 2024) with
  "30–45 days" delivery, i.e. they price registration in 2027 — a defensible, conservative choice for cars ordered now.
  Until the code is fixed: for 2024 cars quote both 50 MRP (release ≤ 31.12.2026) and 500 MRP (release in 2027); for 2025 cars
  0.25 MRP in 2026 vs 50 MRP in 2027. The new code's own text was still not readable on adilet (JS-only page).
- **2026-11-14, Russia (draft, no profile change):** Minpromtorg's draft of new recycling-fee rules (regulation.gov.ru
  02/07/11-26/00172688, published 10.11.2026; autonews.ru 11.11) keeps base rates but makes the personal-use rate conditional:
  GIBDD registration within 1 calendar month of the TPO and 12 months of ownership, otherwise the fee is recalculated to the
  commercial rate. Mention it to Russian clients who plan to resell; update `russia.json` only once adopted.
- **2026-11-04, Kyrgyzstan sanity check:** an exporter's published itemized example (SH GLOBAL, 10.04.2026) — Tucson 2.0 2022,
  FOB $15 500 → ≈$25 430 landed in Bishkek (ETS €2.7/cm³ ≈ $5 830). Our calculator: $26 608 (+4.6%); the ETS line matches, the gap is
  freight ($3 000 vs $2 300) and our $800 service fee. The Kyrgyzstan profile is in the right range.
