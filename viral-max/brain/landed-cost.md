# Landed Cost: what a car really costs delivered to the client's city

Use `viral-max/tools/landed_cost.py` to calculate. This file explains the logic.

## Formula

```
A. KOREA SIDE (paid in KRW, converted to USD)
   Car price (dealer / auction hammer)
 + Auction or buyer fee
 + Deregistration and export documents
 + Inland transport to port (Incheon / Pyeongtaek / Busan)
 + Export customs, port handling, loading/lashing
 = FOB price (car on board in Korea)

B. SEA FREIGHT
 + Ocean freight (container share or RoRo per car)
 + Marine insurance (~0.5–1.5% of value)
 = CIF price (car at destination port). Most customs duties are calculated on this.

C. DESTINATION
 + Port/terminal charges and unloading
 + Import duty (% of CIF or per cc / per year of age) [VERIFY per country]
 + Excise tax (often by engine cc) [VERIFY]
 + VAT (on CIF + duty + excise) [VERIFY]
 + Recycling or other fees [VERIFY]
 + Customs broker, certification, registration
 + Inland transport from port to client city
 = Landed cost in client's city

D. YOUR SERVICE FEE / margin
 = PRICE TO CLIENT
```

## Rules

- **Always ask:** client country and city, car model, year, engine (cc and fuel), mileage, budget.
- The destination tax profile lives in `viral-max/tools/destinations.json`. Fill in your real numbers
  once and the agent reuses them. The numbers shipped there are **placeholders**.
- Exchange rates change daily, so update `krw_per_usd` before quoting.
- On camera, show the breakdown as a "receipt". It is the most trusted and most saved format.
