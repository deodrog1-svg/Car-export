---
description: Ready video caption with delivered prices in 4 countries (Kazakhstan, Kyrgyzstan, Georgia, Russia)
argument-hint: <car: model, year/month, fuel, cc, hp, price in ₩> [+ which video]
---
Use the viral-max agent. Build a compare request JSON in `viral-max/quotes/` with this car and
"destinations": [{"country": "kazakhstan", "city": "Алматы"}, {"country": "kyrgyzstan", "city": "Бишкек"},
{"country": "georgia", "city": "Тбилиси"}, {"country": "russia", "city": "Владивосток", "shipping": "roro"}]
(add more countries only if the user asks). Update exchange rates in `viral-max/tools/costs.json` first if they are older than 1 day.
Run `python3 viral-max/tools/landed_cost.py <request.json>`. Reply in Russian with: the ready caption text block
(copy-paste ready, plus 4–6 hashtags with #казахстан #алматы), one line on which country is most profitable and
why, and the comparison PDF. If the user named a video, adapt the first caption line to it.

Car: $ARGUMENTS
