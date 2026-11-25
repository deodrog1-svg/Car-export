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
- **2026-11-15, Kazakhstan: competitor ETS base is the reference customs value, not the purchase price ([VERIFY] with a broker):**
  encar.youcar.kz states "Растаможка считается по справочной стоимости ГТС", and the 14.11 cards match that. BMW 630i GT 2023: Korea
  $40 054, ETS "48% от стоимости" = $33 556, i.e. 48% of ≈$69 900, so the reference value is **above** the price paid. Genesis GV80 2.5T 2024:
  Korea $49 048, ETS = the 5.5 €/cm³ minimum ($15 590), so the reference value is **below** the price paid. That explains the
  "48% doesn't match" notes of 11–12.11. Our calculator applies 48% to the purchase price, so for cars under 3 years our ETS can be off
  in either direction. Until a broker confirms which base KGD uses, tell under-3-year clients the ETS line is based on the price paid and
  may change after customs valuation. **Code not changed.**
- **2026-11-15, Kazakhstan registration (youcar shift is systematic):** youcar's 14.11 cards charge 50 MRP (216 250 ₸) for a **2025** Avante,
  500 MRP for 2024 cars (Jetta, GV80) and 250 MRP for a 2024 EV (Ioniq 5). That is the calendar-year rule applied as of 2027 (one band older than
  2026). So youcar prices every order as if registration happens after 01.01.2027. Same advice as on 14.11: quote both bands for 2024–2025 cars.
  Our `landed_cost.py` (day count) is still the outlier. **Owner decision pending, code not changed.**
- **2026-11-16, Kazakhstan/EAEU customs value base for personal-use cars (legal text found; practice [VERIFY] with a broker):**
  EAEU Customs Code **art. 267** ("Стоимость товаров для личного пользования", consultant.ru): p. 1 says the value is declared from the
  purchase documents (receipts, invoices etc.) and **transport and insurance are NOT included**. P. 3 lets customs set the value from its
  own price information only when (1) the documents are missing, (2) the goods can't be matched to the documents, (3) there are reasonable
  grounds to doubt the documents and the person does not prove them, or (4) **the declared value does not match the market value of similar goods
  in the country of purchase**. P. 4 says the sources are catalogs and websites of foreign sellers. KGD practice (nur.kz/kapital.kz explainers,
  undated in search): if the declared price is far below the KGD range, the declarant must show the export declaration, invoice, contract,
  bank transfer and auction sheet, and then the declarant's value is accepted. So youcar's "справочная стоимость ГТС" (15.11 entry) is a
  conservative assumption, not the only legal base. A fully documented purchase price should stand **unless it is below the Korean market**
  (e.g. a cheap auction buy), in which case customs can lift it to the market level. Our calculator (ETS on the car price only, no freight
  or insurance) **matches p. 1**. How to quote under-3-year cars: give the ETS on the documented price and warn that it can rise to the
  market/reference value if the price is below the Korean market. Keep the invoice, export declaration, contract, bank transfer and auction sheet.
  The old tks.ru Eurotax rule for *new* cars is Russian practice and is not applied here. **Code not changed** (owner decision pending).
- **2026-11-17, Kazakhstan (youcar cards created 17.11 Seoul, rate 443.20 ₸/$; findings only, code not changed):**
  (1) **Hybrids again get EV registration rates:** Carnival 1.6T HEV 2025 — 108 125 ₸ (25 MRP, the EV rate for 2–3 years, i.e. the 2027 band),
  Grandeur IG 2.4 HEV 2021 — 1 081 250 ₸ (250 MRP, half of 500). kolesa.kz's table excludes hybrids from the EV discount, so quote hybrids at the
  full ICE rate unless a broker confirms otherwise [VERIFY]. (2) **2023 cars already priced as "3–5 years"** (S 580 L 2023: 3.6 €/cm³;
  M240i 2023: 3 €/cm³), so the age at clearance, not the model year, decides the ETS bracket — same as our day-count logic. (3) **Young big
  engines hit the minimum:** X7 40d 2026 ($104 357 in Korea) pays ETS $50 666 = "не менее 15 €/см³", well above 48% of the price.
  (4) **BMW M2 G87 2026:** ETS $22 164 labelled "48% от стоимости" is only ≈34% of the $65 790 Korean price, so youcar's base is not the purchase
  price here [VERIFY with a broker; compare our task 004 quote before reusing it]. (5) **Payment order for individuals** (Ministry of Industry
  via zakon.kz, 01.10.2026): СБКТС → recycling fee **and first-registration fee** → customs clearance → state registration. If the registration
  fee is paid before customs, the fee band may be fixed on the payment date, which matters for 2024–2025 cars around 01.01.2027 [VERIFY].
- **2026-11-18, Kazakhstan (youcar cards 13–18.11 Seoul, rate 442.48 ₸/$; findings only, code not changed):**
  (1) **Hybrids pay far less ETS than the €/cm³ minimum in youcar cards:** Grandeur 1.6T HEV 2026 ($39 349): ETS $6 012 (≈15% of price);
  Sorento 1.6T HEV 4WD 2026 ($41 248): ETS $6 994 (≈17%). The diesel Sorento 2.2D 2026 ($34 588) pays $13 366 (min 5.5 €/cm³), so the hybrid ends
  **cheaper turnkey (24.60 vs 24.79 M ₸)** although it costs $6.7k more in Korea. ETS (Decision 107) covers all of heading 8703 and the cards
  give no legal basis for the lower hybrid line. Our calculator applies normal ETS to hybrids. Ask a broker before quoting a hybrid below the
  €/cm³ minimum [VERIFY]. (2) **ETS lines that don't match their labels:** Audi Q8 50 TDI 2026 ($95 363): ETS $36 159 labelled "48%" (≈38%,
  and below the 15 €/cm³ minimum youcar used for X7 40d on 17.11); Kia K5 1.6T 2023 ($14 759): $4 915 labelled "54%" (≈33%). Treat youcar
  ETS lines as unreliable for young cars. (3) **Registration bands seen today:** 2026 cars — 1 082 ₸ (0.25 MRP); 2023 cars — 2 162 500 ₸
  (500 MRP), which is above the K5's whole ETS. (4) **Over-5-year cars "только на ИП":** S 560 L 2018 — customs (ИП) $15 975, GLS 580 2020 — $25 104,
  both with registration 2 162 500 ₸ + recycling fee 2 486 875 ₸ (4.0 L). Our calculator has no ИП mode. Don't quote over-5-year cars to
  individuals after 30.12.2026.
- **2026-11-19, Kazakhstan hybrids — is there an official lower duty? (legal check; findings only, code not changed):**
  **No official reduced ETS line for hybrids imported by individuals was found.** Decision 107 ETS covers heading 8703 by engine volume, and
  KZ explainers (kolesa.kz 30.09/07.10.2026) list no hybrid exception. Only two official hybrid rules exist, both for declaration on a ДТ
  (goods declaration), not the ПТД/ETS route: (1) **serial hybrids EREV, codes 8703 80 000 3/4/5/8 — 0% duty under the KZ WTO exemption list
  from 22.01.2026** (EEC Council decision of 23.12.2025; kolesa.kz) + VAT 16%, recycling fee and registration still due; (2) **parallel hybrids
  where the ICE is stronger than the 30-minute electric-motor power go under a code with 15% duty** — KGD back-charged 421 importers for
  563 BYD Destroyer 05 cars declared at 0% (newtimes.kz, 01.07.2026). Korean 1.6T HEVs (180 hp ICE, ~44–54 kW motor) are parallel hybrids
  with the stronger ICE, so neither 0% nor anything below the normal ETS applies on the ETS route. New youcar cards (19.11 Seoul, 443.32 ₸/$):
  Grand Koleos 1.5 E-Tech 2024 ($25 755) — ETS $6 080 (≈24%), Staria HEV 2025 ($24 543) — $7 006 (≈29%); no VAT line, so this is not a
  "15% + VAT 16%" ДТ calculation either; registration again at EV rates (250 / 25 MRP). Per cm³ the youcar hybrid lines are ≈3.4–4.0 €/cm³,
  i.e. they look like a per-cm³ rate rather than 48% of price, with no legal basis found [VERIFY with a broker]. **Quote hybrids with normal
  ETS (as the calculator does) and warn about back-charge risk if a competitor quotes lower.** Same day, a 3–5-year car beats a young one on
  ETS: X5 30d 2022 ($54 539) pays $10 153 (3 €/cm³) vs GLB 200d 2025 ($39 389) $17 631 (48%) — consistent with our calculator's age brackets.
- **2026-11-20, Kazakhstan (youcar cards created 20.11 Seoul, rate 448.87 ₸/$; findings only, code not changed):**
  (1) **Same year, same body, 13 M ₸ apart because of the ETS base.** Mercedes E 250 W213 2023 ($31 014) shows ETS **$36 788** labelled
  "до 3 лет · 48%" — more than the car's price (48% of the invoice would be ≈$14 900), so the base must be ≈$76.6k, i.e. the reference
  customs value, not the purchase price (same pattern as 630i GT 2023 on 15.11) [VERIFY with youcar/broker]. Total 35.88 M ₸ vs
  E 350 4MATIC 2023 ($25 395, ETS $12 911) at 22.64 M ₸. Our calculator uses the purchase price (ТК ЕАЭС art. 267); before quoting a young
  Mercedes/BMW, warn the client that KGD may apply a higher reference value. (2) **Registration by year confirmed again:** 530i G60 2024
  ($37 914) pays 2 162 500 ₸ (500 MRP), 530i G60 2025 ($45 117) 216 250 ₸ (50 MRP); ETS identical ($12 415, 5.5 €/cm³). Turnkey gap
  only 1.29 M ₸ for a $7.2k price gap. (3) **Hybrids again at half registration:** Sorento 1.6T HEV 2023 — 1 081 250 ₸ vs 2 162 500 ₸ for
  petrol E 350 2023; ETS $4 618 "по возрасту и объёму" (≈16% of price). No legal basis found (see 19.11) [VERIFY]. (4) **>3.0 L pays twice:**
  Palisade 3.8 2022 ($18 115): ETS $15 352 (3.6 €/cm³) + recycling 2 486 875 ₸ + registration 2 162 500 ₸ → 22.2 M ₸ (×2.73);
  Carnival 3.5 2024 ($26 919): ETS $13 715 (labelled "до 3 лет, не менее 3.5 €/cm³") → 26.09 M ₸. Palisade 2.5T HEV 2025 ($40 568):
  ETS $11 130, registration 108 125 ₸ → 26.93 M ₸ (+48%). (5) FX: youcar moved 443.32 → 448.87 ₸/$ (+1.25%); NBK 20.11 = 448.72 ₸/$
  (+0.9% vs 12.11). EUR/USD vs 12.11: +1.1–1.45% depending on source (CBR 20.11 0.912 €/$, ECB 19.11 0.910) — under the 1.5% threshold,
  `costs.json` unchanged.
- **2026-11-21, Kazakhstan / Kyrgyzstan / Georgia / Russia (youcar cards created 20–21.11 Seoul, rate 454.27 ₸/$; findings only, code and JSON not changed):**
  (1) **2027–2029 budget law passed parliament:** Kurultai approved it in 2nd and adopted it in 3rd reading on 18.11.2026 (zakon.kz,
  forbes.kz); MZP raised to 110 000 ₸ in the 2nd reading. MRP 4 693 ₸ from 01.01.2027 is confirmed only in the Minfin draft; the
  adoption news does not quote it and no presidential signature was found [VERIFY]. When confirmed: registration >3 yrs 500 MRP =
  2 346 500 ₸, recycling fee 2–3 L 175 MRP = 821 275 ₸ — update `kazakhstan.json` for vehicles released from customs in 2027.
  (2) **Petrol vs hybrid, same model, same price in Korea:** Palisade LX3 2.5T 2026 ($40 800) — ETS $18 777 ("до 3 лет · 48%"), total
  30.71 M ₸; Palisade 2.5T HEV 2025 ($40 568, 20.11) — ETS $11 130, total 26.93 M ₸. Sorento HEV 2024 ($33 867) — ETS $5 301 (≈16%),
  registration 1 081 250 ₸ (half). Still no legal basis for the lower hybrid line (see 19.11) — keep quoting hybrids with normal ETS.
  (3) **ETS below the stated 48%:** X5 30d 2026 ($70 460) shows $28 951 "48% от стоимости" = 41% of the card price; Palisade 2026 46%.
  Base appears to differ from the card price (maybe price excl. something or a different FX) [VERIFY]. Our calculator is more conservative here.
  (4) **New car registration again 1 082 ₸ (0.25 MRP)** for 2026 cars; 2025 — 216 250 ₸; 2024 (E 450) — 2 162 500 ₸, consistent with
  20.11. **520i G30 2021 is already shown as "Таможенный платёж (ИП)" $4 956** — youcar treats a 2021 car as over 5 years for individuals.
  (5) **FX:** youcar 448.87 → 454.27 ₸/$ (+1.2% in a day, +2.5% since 19.11). No NBK figure for 21.11 found; `costs.json` untouched
  (owner updated it).
  (6) **Kyrgyzstan body-import ban:** no signed extension found by 21.11. Resolution No. 357 (20.05.2026) was published 22.05 and the
  ban starts 3 days after entry into force for 6 months (kaktus.media, 24.05), so the end could be ≈25.11, not 22.11 [VERIFY]. Affects
  only bodies (8707 10 900 0), not whole cars — `kyrgyzstan.json` unchanged.
  (7) **Georgia:** from 16.11.2026 a 450 ₾ fee per car for customs clearance of **re-export** (Minfin of Georgia, Revenue Service;
  lada.kz 18.11 citing NewsGeorgia); exempt — cars sold abroad after first registration in Georgia and after temporary import. Does not
  apply to import into Georgia (our Tbilisi quotes unchanged), but adds ≈$173 to Korea → Poti → Central Asia transit deals.
  (8) **Russia:** exporters already print two prices — TAauto BMW X4 20i 2022: 5.53 M ₽ now, 5.73 M ₽ from 01.01.2027 (+3.6%), in line
  with the +10–20% recycling-fee indexation (decree 1255). Draft rules of 10.11 unchanged.
- **2026-11-22, Kazakhstan / Kyrgyzstan / Russia (youcar cards created 20–21.11 Seoul, rate 453.83 ₸/$; findings only, code and
  country JSON not changed; `costs.json` KZT only):**
  (1) **FX:** NBK official rate 21.11 and 22.11.2026 = **455.00 ₸/$** (nationalbank.kz rss; 12.11 was 444.76, +2.3% > 1.5% threshold)
  → `costs.json` KZT set to 455.0. Other rates untouched (owner updated them 20.11).
  (2) **Budget 2027–2029:** still no presidential signature found; MRP 4 693 ₸ remains a draft figure [VERIFY]. Order No. 293
  (Euro-5, ≤5 yrs from 30.12.2026): no new text found. `kazakhstan.json` unchanged.
  (3) **youcar ETS base ≠ purchase price (strongest evidence so far):** E 200 W214 2026 ($43 529) — ETS $55 920 labelled
  "до 3 лет · 48%" (= 48% of ≈$116.5k, total 48.45 M ₸); E 450 W214 2026 ($63 792) — ETS $19 606 (48% of ≈$40.8k, 41.49 M ₸);
  X5 40i 2026 ($99 066) — $27 897 (48% of ≈$58.1k); Sorento 2.2D 2025 new ($43 454) — $8 744 (48% of ≈$18.2k); Palisade HEV 2WD
  2026 ($42 403) — $13 083. The base is clearly an internal/reference valuation, not the card price, in both directions. Under
  TC EAEU art. 267 the base is the transaction value with documents [VERIFY KGD practice]. **Our calculator keeps the purchase price.**
  When a client shows a competitor's quote, compare the implied base (ETS ÷ 0.48) first.
  (4) **Minimum €/cm³ applied instead of 48%:** X5 30d 2025 ($64 543) — $25 274 "не менее 7.5 €/см³" (= 7.5 × 2 993 cm³ at ≈1.126 $/€),
  although 48% of the card price would be ≈$31k. Same for X5 M60i 2024 (4.4 L) — $37 086 "не менее 7.5 €/см³"; recycling fee for
  >3 L 2 486 875 ₸ and registration 2 162 500 ₸.
  (5) **Over-5-year car:** X5 30d 2020 — "Оформление только на ИП", line "Таможенный платёж (ИП)" $8 749, registration 2 162 500 ₸.
  Registration pattern unchanged: 2026 — 1 082 ₸, 2025 — 216 250 ₸ (HEV 2025 — 108 125 ₸), 2023 — 2 162 500 ₸.
  (6) **Kyrgyzstan body ban:** no signed extension found on 22.11 (only the Minekonomiki draft of 20.10: new resolution would enter
  into force 10 days after publication + 3 days). Check again 24–26.11 [VERIFY]. `kyrgyzstan.json` unchanged (bodies only).
  (7) **Russia sanity check:** ASIA EXPRESS Sonata 2.0 2022 (160 hp) — 2.30 M ₽ turnkey RF; our real deal Sonata 2023 — 2.35 M ₽
  (Vladivostok). TAauto K3 1.6 2023 — 1.78 M ₽ Vladivostok (broker fee absorbed until 31.12.2026).
- **2026-11-23, all markets (findings only; code, country JSON and `costs.json` not changed):**
  (1) **FX:** NBK official rate 23.11.2026 = 455.00 ₸/$ (unchanged vs 21–22.11; KRW 33.98 ₸/100 → ≈1 339 ₩/$). CBR 21.11:
  82.19 ₽/$, KGS 87.45, GEL 2.593, EUR 0.910, KRW ≈1 331. All within 0.5% of `costs.json` → no update.
  (2) **Kazakhstan:** budget 2027–2029 still not signed in search results (last step: Kurultai 18.11); MRP 4 693 ₸ stays a draft
  [VERIFY]. Order No. 293 (Euro-5, ≤5 yrs from 30.12.2026): no new text. `kazakhstan.json` unchanged.
  (3) **Kyrgyzstan body ban (8707 10 900 0):** no signed extension found on 23.11 (Seoul). The kaktus.media "Кабмин продлил запрет…"
  hit is the old 07.10.2025 article (Resolution No. 633), not a new one. Ban under No. 357 ends 22–25.11; check 24–26.11 [VERIFY].
  Whole cars are not affected. `kyrgyzstan.json` unchanged.
  (4) **Georgia / Russia:** no new rules (Georgia excise since 02.04.2026, re-export fee 450 ₾ since 16.11; Russia: +10–20% recycling
  fee from 01.01.2027 per the 2024 schedule, Minpromtorg draft of 10–12.11 still a draft).
  (5) **Market check, Kazakhstan resale vs exporter quotes:** kolesa.kz "из Кореи" listings 22.11: Santa Fe MX5 2.5 05/2025 (24.5k km) —
  21.0 M ₸ resale vs youcar turnkey Santa Fe MX5 2024 — 22.9 M ₸ (16.11). Already-imported Korean cars are now priced near the
  turnkey level, so the import argument for Almaty is "newer/cleaner + your own documents", not "much cheaper" [VERIFY per model].
- **2026-11-24, all markets (youcar cards created 23–24.11 Seoul, rate 453.85 ₸/$; findings only, code, country JSON and
  `costs.json` not changed):**
  (1) **FX:** NBK official rate 24.11.2026 = 455.12 ₸/$ (KRW 33.81 ₸/100 → ≈1 346 ₩/$); CBR 24.11: 82.15 ₽/$, KGS 87.45, GEL 2.593,
  EUR 0.910, KRW ≈1 337. All within 1% of `costs.json` → no update.
  (2) **Kazakhstan:** budget 2027–2029 still not signed in search results (24.11; last year's was signed 08.12.2025); MRP 4 693 ₸
  stays a draft [VERIFY]. Order No. 293 (Euro-5, ≤5 yrs from 30.12.2026): nothing new. `kazakhstan.json` unchanged.
  (3) **youcar.kz is back (HTTP 200 on 24.11).** Fixed lines unchanged: Korea costs $800, freight $2 600 (sedan/SUV) or $2 800
  (minivan, X6, GLS), broker $300, SBKTS + GLONASS $400, SVH $100 + $100, import $70, transfer $100, recycling check $100, EPTS $200,
  plates 12 000 ₸, tech passport 5 000 ₸, company fee $700 (≈$2 000 local services + fee on top of duty/recycling/registration).
  (4) **ETS base again ≠ purchase price:** BMW Z4 sDrive20i 2025 ($37 586) — ETS $38 457 "до 3 лет · 48%" (= 48% of ≈$80.1k, more
  than the car itself; total 38.09 M ₸, ×2.23). Kia K8 3.5 2025 ($28 941) — $21 472 "не менее 5.5 €/см³" (= 5.5 × 3 470 cm³), plus
  recycling fee >3 L 2 486 875 ₸ (total ×2.15). GLS 580 2024 — $67 078 "не менее 15 €/см³". Meanwhile 3–5-year cars pay by volume:
  Cayenne 3.0 2023 ($69 159) — ETS $10 139, total 41.84 M ₸ (+33%); X6 40i 2022 — $10 149 (+54%). Practical rule for Almaty quotes:
  **2022–2023 cars with 2–3 L engines have the lowest markup; young cars over 3 L or with a high reference value are ×2+.**
  (5) **Registration anomalies [VERIFY]:** Audi Q3 2024 charged 500 MRP (2 162 500 ₸) although "до 3 лет" ETS was applied — possibly
  an early production date. Hybrids 2023 (Grandeur 1.6 HEV, Panamera 4 E-Hybrid) — 1 081 250 ₸ (250 MRP, half rate), same pattern as
  before; our calculator still treats hybrids as ICE.
  (6) **Over-5-year cars ("только на ИП"):** Carnival 2.2D 2021 — "Таможенный платёж (ИП)" $2 922; G80 2.5T 2020 — $6 105.
  (7) **Kyrgyzstan body ban (8707 10 900 0):** term under Resolution No. 357 ended 22.11 (economist.kg); no signed extension found on
  24.11 (24.kg, economist.kg, kaktus.media) — status "lapsed or not yet published" [VERIFY cbd.minjust.gov.kg]. Whole cars are not
  affected. `kyrgyzstan.json` unchanged.
  (8) **Georgia / Russia:** no new rules. Russia: Minpromtorg draft of 10.11 still a draft; +10–20% recycling fee from 01.01.2027 per
  the 2024 schedule.
- **2026-11-25, all markets (youcar cards created 25.11 Seoul, rate 458.35 ₸/$; findings only, code, country JSON and
  `costs.json` not changed):**
  (1) **FX:** NBK official rate 25.11.2026 = 458.28 ₸/$ (EUR 501.45, RUB 5.59, KRW 34.13 ₸/100 → ≈1 343 ₩/$, ≈0.914 €/$, ≈82.0 ₽/$).
  KZT +0.7% vs `costs.json` (455.0), KRW +0.6%, EUR +0.7% → below the 1.5% threshold, no update.
  (2) **Kazakhstan:** budget 2027–2029 still not signed in search results on 25.11 (forbes.kz, prg.kz; last stage — Kurultai 18.11);
  MRP 4 693 ₸ stays a draft [VERIFY]. Euro-5 / ≤5 yrs order (in force 30.12.2026): only old retellings (Interfax 02.11, lada.kz);
  the number 293 still not confirmed by an open source [VERIFY adilet]. `kazakhstan.json` unchanged.
  (3) **youcar: big engine vs year, same model (Carnival 3.5 V6 petrol).** 2023 Noblesse ($22 157) — ETS "3–5 лет · 3.6 €/см³"
  $14 067, recycling >3 L 2 486 875 ₸, total 23.97 M ₸ (×2.36). 2021 Signature ($20 655, "только на ИП") — customs payment (IP)
  only $4 945, total 19.10 M ₸ (×2.02). For over-3-L engines the 3–5-year ETS per cm³ is far above youcar's IP line [VERIFY the IP
  rate basis with a broker]. Hyundai Staria 3.5 LPi Cargo 2024 ($18 402): ETS "до 3 лет · не менее 5.5 €/см³" $21 461 > car price,
  total 25.64 M ₸ (×3.04); youcar treats the cargo van as M1 with the >3 L recycling fee [VERIFY N1 category].
  (4) **Over-5-year cars via IP (youcar 25.11):** GLS 400 d 2020 — IP payment $24 059 (≈63% of the $38 298 price, diesel 2.9 L);
  S 350 d 2017 — $9 225; Cayenne GTS 3.6 2017 — $11 669; A5 45 TFSI 2020 — $4 706; Tucson 1.6T 2021 — $3 112. The IP line is not a
  flat €/cm³; our calculator has no IP mode (owner decision).
  (5) **EV check:** Casper Electric 2024 ($17 651) — ETS $2 612 (≈15%), recycling 0, registration 1 081 250 ₸ (half rate), total
  13.0 M ₸ (+61%) — consistent with the EV notes of 04.11.
  (6) **Kyrgyzstan body ban (8707 10 900 0):** still no signed extension in search results on 25.11 (24.kg, economist.kg,
  kaktus.media — only the 20.10 draft). Status "lapsed or not yet published" [VERIFY cbd.minjust.gov.kg]. `kyrgyzstan.json` unchanged.
  (7) **Georgia / Russia:** no new rules (Georgia: excise since 02.04.2026, re-export fee since 16.11; Russia: draft of 10.11 still a
  draft, +10–20% from 01.01.2027 per the 2024 schedule).
- **2026-11-26, all markets (youcar cards created 26.11 Seoul, rate 455.98 ₸/$; findings only, code, country JSON and
  `costs.json` not changed):**
  (1) **FX:** NBK official rate 26.11.2026 = 458.57 ₸/$ (KRW 34.13 ₸/100); CBR 26.11: 82.31 ₽/$, 87.45 KGS/$, 2.592 GEL/$,
  ≈1 344 ₩/$, 0.912 €/$. All within 1% of `costs.json` (KZT +0.8%, KRW +0.6%, EUR +0.5%) → no update.
  (2) **Kazakhstan rules:** budget 2027–2029 still not signed in search results on 26.11 (only Kurultai 18.11); MRP 4 693 ₸ stays a
  draft [VERIFY]. Euro-5 / ≤5 yrs order: nothing new (30.12 per Interfax, 31.12 per lada.kz). `kazakhstan.json` unchanged.
  (3) **ETS check, 3–5 years per cm³ — matches:** Palisade 3.8 2021 (3 778 cm³) — youcar ETS "3–5 лет · 3.6 €/см³" $15 298
  (3 778 × 3.6 = 13 601 € → implied ≈1.125 $/€). Our table gives the same line.
  (4) **ETS lines youcar does not explain [VERIFY with a broker]:** BMW 520i G60 2026 ($41 217) — label "до 3 лет · 48%", but the
  line is $14 217 (≈34.5% of price; implied base ≈$29.6k). 520i G60 2025 ($38 969) — "не менее 5.5 €/см³" $12 371 (1 998 cm³ × 5.5 =
  10 989 € ✓). Palisade LX3 HEV 2025 ($32 599) — ETS $11 129 (≈34%; below the 5.5 €/cm³ minimum of ≈$15.5k for 2 497 cm³),
  registration 108 125 ₸ (EV/hybrid half rate). Santa Fe TM 1.6 HEV 2023 — $3 907 (≈2.2 €/cm³; table 3–5 yrs 1.5–1.8 L says
  2.5 €/cm³). Panamera 4 E-Hybrid 2021 (2 894 cm³) — $13 721 (≈4.2 €/cm³; table says 3.0 €/cm³ for 2.3–3.0 L), registration
  1 081 250 ₸ (half rate). Hybrids keep getting non-table ETS lines and half-rate registration in youcar cards; our calculator
  treats hybrids as ICE — keep it until a broker confirms.
  (5) **IP-only cars (youcar 26.11):** GLE 450 2019 — IP payment $9 521 (≈36% of $26 604); Santa Fe 2.2D 2019 — $2 593;
  G 63 2021 — $33 534 (≈28% of $118 031); Carnival 2.2D 2018 — $2 388 (but registration 2 162 500 ₸ + recycling 1 081 250 ₸ =
  $7 114 ≈ the car price $7 194). Still no IP mode in the calculator (owner decision).
  (6) **Kyrgyzstan / Georgia / Russia:** no new rules (no signed body-ban extension found on 26.11 [VERIFY cbd.minjust.gov.kg];
  Georgia excise since 02.04, re-export fee since 16.11; Russia draft of 10.11 still a draft).
- **2026-11-04, Kyrgyzstan sanity check:** an exporter's published itemized example (SH GLOBAL, 10.04.2026) — Tucson 2.0 2022,
  FOB $15 500 → ≈$25 430 landed in Bishkek (ETS €2.7/cm³ ≈ $5 830). Our calculator: $26 608 (+4.6%); the ETS line matches, the gap is
  freight ($3 000 vs $2 300) and our $800 service fee. The Kyrgyzstan profile is in the right range.
