---
description: Calculate a Korean car's full delivered price to a client's city
argument-hint: <car, year, price in KRW, engine cc, destination>
---
Calculate the landed cost with `python3 viral-max/tools/landed_cost.py` (see `viral-max/brain/landed-cost.md`). If the destination isn't in `viral-max/tools/destinations.json`, research its current import duty, excise, VAT and fees, mark unverified numbers [VERIFY], and ask before adding them. Present the result as a clean "receipt" ready to show on camera.

Request: $ARGUMENTS
