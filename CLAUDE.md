# Car Export: Viral Max

This repo is the home of **Viral Max**, an AI social media marketing agent for a South Korea car export company.

- Agent definition: `.claude/agents/viral-max.md`
- His knowledge ("brain"): `viral-max/brain/`
- User's teaching space: `viral-max/teach/lessons.md`
- User's adjustment space (overrides everything): `viral-max/improve/adjustments.md`
- Video results he learns from: `viral-max/improve/performance-log.md`
- Daily research log: `viral-max/daily-learning/trend-log.md`
- Market intel (ideal client, focus cars): `viral-max/market-intel/` (`insights.md`, `export-deals.csv`, `our-deals.csv`)
- Deliverables: `viral-max/tasks/NNN-*.md`
- Broker calculator: `python3 viral-max/tools/landed_cost.py <request.json>` → Russian PDF quote in `viral-max/quotes/`
  (own costs + FX in `viral-max/tools/costs.json`, customs rules per country in `viral-max/tools/countries/`, method in `viral-max/brain/landed-cost.md`)

For any marketing, content, video, or car price / customs quote request, delegate to the `viral-max` agent.
Never delete content from `teach/` or `improve/`. Only append or edit as instructed.
