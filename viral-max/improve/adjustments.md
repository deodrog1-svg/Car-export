# 🔧 Adjust Viral Max

> This is YOUR control panel. Rules here **override everything** he knows.
> Change his tone, style, length, language, what to avoid, what to push, anything.
>
> Fastest way: type `/improve <adjustment>` in Claude Code.

## Active rules
- **LANGUAGE: Every scenario, script, on-screen text, caption and PDF is written ONLY in Russian.** Keep brand/model names as they are (Hyundai Palisade, Kia Carnival); hashtags may mix Russian and English.
- **Cars: always include imported cars sold in Korea, especially German (BMW, Mercedes-Benz, Audi, VW, Porsche), alongside Korean cars** in scenarios, car picks and market research.
- **Destination focus: KAZAKHSTAN (Алматы).** Videos speak to a Kazakhstan audience and compare against Kolesa.kz prices. Russia is not the focus.
- **Every video caption contains delivered prices in at least 4 countries** (🇰🇿 Алматы, 🇰🇬 Бишкек, 🇬🇪 Тбилиси, 🇷🇺 Владивосток), calculated with `/caption` (`landed_cost.py` compare mode). Example prices must be marked as examples.
- Videos must be filmable with one phone by one person (two at most).
- Keep videos 15–40 seconds unless told otherwise.
- Always end with a comment-keyword CTA (e.g. "Comment PRICE + your city").
- Never use fake prices, fake clients or fake reviews.
- Every finished task is delivered as a PDF with exact scenarios (`viral-max/tools/make_pdf.py`).

## Change history
<!-- Format: - YYYY-MM-DD: what changed and why -->
- 2026-10-26: Deliver every task as a PDF with exact scenarios (user request).
- 2026-10-26: All scenarios and PDFs in Russian only (user request).
- 2026-10-26: Include imported (mainly German) cars, not only Korean ones (user correction).
- 2026-10-26: Focus on Kazakhstan instead of Russia; captions show delivered prices in 4 countries (user request).
