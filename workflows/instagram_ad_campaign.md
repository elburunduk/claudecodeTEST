# Workflow: Instagram & Facebook Ad Campaign Generator

## Objective
Given a digital product (PDF), generate 5 ready-to-run Instagram/Facebook ad campaigns — including hooks, body copy, CTAs, visual direction, and audience targeting — and export everything to a Google Sheet.

## Inputs
| Input | Source | Notes |
|-------|--------|-------|
| `product_price` | Provided by user at runtime | e.g. `9`, `17`, `27` |
| `beacons_url` | Provided by user at runtime | Full beacons.ai product link |
| `SERPER_API_KEY` | `.env` | For competitor research |
| `ANTHROPIC_API_KEY` | `.env` | For campaign generation |
| `GOOGLE_SHEET_ID` | `.env` | Target sheet for output |
| `credentials.json` | Project root | Google OAuth |

## Steps

### Step 0 — Pre-flight check (manual, one-time)
Before spending any ad money:
1. Install Meta Pixel in beacons.ai → Settings → Integrations → Meta Pixel
2. Create a Meta Business Manager account if not done
3. Set up a Facebook Page connected to the Instagram account
4. Confirm `credentials.json` is present in project root (Google OAuth)

### Step 1 — Competitor Research
- **Tool:** `tools/research_competitors.py`
- **Command:** `python tools/research_competitors.py`
- **Output:** `.tmp/competitor_research.json`
- Searches Serper for similar mom wellness digital products, hooks, pricing, and visual styles

### Step 2 — Generate Ad Campaigns
- **Tool:** `tools/generate_ad_campaigns.py`
- **Command:** `python tools/generate_ad_campaigns.py --price 17 --url "https://beacons.ai/..."`
- **Output:** `.tmp/campaigns.json`
- Uses Claude to generate 5 campaigns informed by competitor research and product analysis

### Step 3 — Export to Google Sheets
- **Tool:** `tools/export_to_sheets.py`
- **Command:** `python tools/export_to_sheets.py`
- **Output:** Shareable Google Sheet URL printed to console
- Writes two tabs: **Campaigns** and **Competitor Intel**

## Expected Output
A Google Sheet with:
- Tab 1 "Campaigns": 5 rows, one per campaign — name, hook, body copy, CTA, visual direction, placement, audience, budget note
- Tab 2 "Competitor Intel": competitor product names, hooks observed, price points, positioning notes

## Budget Strategy for <$100/mo
- **Do NOT run all 5 campaigns at once**
- Week 1–2: Campaign 1 + Campaign 2 at $3/day each (~$42)
- Week 3–4: Kill the loser, test Campaign 3 at $3/day (~$21)
- Remaining ~$37: Boost 1–2 best-performing organic Instagram posts
- After 30 days: review CPM, CTR, and cost-per-click to decide what to scale

## Recommended Campaigns (pre-analyzed from product)
1. **Permission Hook** — "You're not lazy. You're running on empty." (cold traffic)
2. **Social Proof** — "10,000 exhausted moms started this..." (cold traffic, broad)
3. **Identity Mirror** — "If you wake up tired before the day even starts..." (warmer audience)
4. **Transformation/Curiosity** — "Imagine waking up 30 days from now — not perfect, but lighter." (Reels)
5. **Personal Story** — Alice's kitchen moment from Week 2 intro (existing followers)

## Edge Cases & Known Issues
- **Google auth expired:** Delete `token.json` and re-run any sheets tool — it will re-authenticate
- **Serper rate limit:** Free tier = 2,500 searches/mo. This workflow uses ~8 per run.
- **beacons.ai Pixel:** Must be installed before running any paid ads or Meta cannot optimize
- **Small budget warning:** At <$100/mo, Meta's algorithm needs ~50 conversions/week to optimize. With low budget, optimize for "Link Clicks" or "Landing Page Views" — NOT "Purchases" — until volume is sufficient

## Learned Improvements
<!-- Updated as workflow evolves. Newest entries at the top. -->
- [2026-03-03] — Initial workflow created for @MOTHER_INBALANCE product launch
