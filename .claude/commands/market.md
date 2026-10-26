---
description: Market intel. Find 15 recently exported Korean cars with delivered price, country and city; update ideal-client analysis
---
Use the viral-max agent. Do the daily market-intelligence research:

1. Find **15 NEW** real examples of cars exported from South Korea (not already in `viral-max/market-intel/export-deals.csv`), preferably from the last 30 days. For each: model, year, engine/hp, price in Korea, **delivered price paid by the client** (под ключ), currency, **country and city**, data type (`реальная сделка` = a delivered car reported by exporter or client; `пример экспортёра` = published turnkey calculation; `объявление продавца` = listing), source date and URL.
   Search in Russian, English and Korean: exporter blogs and sites, VK/Dzen/Telegram previews (tgstat, t.me/s/<channel>), YouTube/RuTube descriptions, drom.ru / auto.ru "под заказ из Кореи", lalafo.kg, kolesa.kz, olx.uz, news ("중고차 수출"), forums. Vary the countries: Russia, Kyrgyzstan, Kazakhstan, Uzbekistan, Tajikistan, Georgia, Armenia, Azerbaijan, Mongolia, Middle East, Africa, plus the client countries in `viral-max/teach/lessons.md` first.
   **Never invent or estimate a row.** If you find fewer than 15 trustworthy examples, add what you found and say how many.
2. Append them to `export-deals.csv` (same columns; use the csv module so quoting stays valid).
3. Rewrite `viral-max/market-intel/insights.md` **in Russian**: market changes, top models (counts across the whole CSV, recent rows weigh more), the ideal client per market, the top 4 focus cars, 3 video ideas from the data, and data gaps. Rows in `our-deals.csv` (our real sales) weigh the most. Update the date and record counts.
4. If a finding changes the broker rules or car knowledge, update `viral-max/brain/` and the country profiles in `viral-max/tools/countries/`.
