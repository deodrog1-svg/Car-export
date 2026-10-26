# 🚗🇰🇷 Viral Max: your viral car-export marketing agent

Viral Max is an AI marketer built into Claude Code. He creates viral, easy-to-film video ideas that
sell your Korea car export services, knows which Korean cars are best to export, and calculates
full delivered prices to your clients' cities.

## Talk to him (in Claude Code, inside this repo)

| Command | What it does |
|---|---|
| `/ideas 10 videos about Genesis GV80 for Kazakhstan` | New video ideas with exact scenarios, saved to `viral-max/tasks/` |
| `/price Carnival 2022, diesel 2151cc 199hp, 41,000 km, ₩32,000,000 → Kyrgyzstan, Bishkek` | **Broker:** exact itemized delivered price as a Russian PDF |
| `/teach my clients are mostly in Uzbekistan and Kyrgyzstan` | **Teach him** (saved forever in `viral-max/teach/lessons.md`) |
| `/improve make all scripts in Russian, max 20 seconds` | **Adjust him** (rules in `viral-max/improve/adjustments.md` override everything) |
| `/results video 001-#1 TikTok 250k views 3k shares 40 DMs` | Tell him how a video did so he learns |
| `/learn` | Make him research today's trends and market right now |
| `/market` | Find 15 recently exported cars (price, country, city) and update the ideal-client analysis |
| `/deal Carnival 2022, client paid $27,500, profit $1,200, Bishkek, family, TikTok` | Record OUR real sale (the most valuable data for him) |

Or just say: *"Viral Max, …"*

## His spaces

```
.claude/agents/viral-max.md      ← his personality and method
viral-max/
  brain/                         ← what he knows (virality, Korean cars, cost formula)
  teach/lessons.md               ← ✍️ YOUR space to teach him
  improve/adjustments.md         ← 🔧 YOUR space to adjust him
  improve/performance-log.md     ← 📊 real results he learns from
  daily-learning/trend-log.md    ← 📈 his daily research
  market-intel/                  ← 🎯 exported cars database + ideal client and focus cars (insights.md)
  tasks/                         ← 🎬 his deliverables
  tools/landed_cost.py           ← 🧮 broker calculator → PDF quote
  tools/costs.json               ← your own costs + exchange rates
  tools/countries/               ← customs rules per country (researched, with sources)
  quotes/                        ← 💵 finished price quotes (PDF)
```

## First task, done ✅
👉 [`viral-max/tasks/001-first-10-viral-videos.md`](viral-max/tasks/001-first-10-viral-videos.md)
