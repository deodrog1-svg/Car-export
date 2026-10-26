---
description: Car broker. Exact delivered price of a Korean car to any country and city, as an itemized Russian PDF
argument-hint: <car (model, year, fuel, cc, hp, mileage, price ₩ or link) + country + city>
---
Use the viral-max agent as a professional car broker. Follow `viral-max/brain/landed-cost.md` exactly:
collect the car data (ask once for anything essential that's missing), update exchange rates, check or
research the country profile in `viral-max/tools/countries/` from official sources, write the request
JSON in `viral-max/quotes/`, run `python3 viral-max/tools/landed_cost.py <request.json>`, sanity-check
against local listings, then send the user the PDF with a short summary in Russian.

Request: $ARGUMENTS
