"""
Step 2: Ad Campaign Generator
Uses Claude to generate 5 complete Instagram/Facebook ad campaigns.
Usage: python tools/generate_ad_campaigns.py --price 17 --url "https://beacons.ai/..."
Output: .tmp/campaigns.json
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import argparse
import json
import anthropic
from _base import env, save_tmp, load_tmp

# ── Product brief (from PDF analysis — update if product changes) ──────────
PRODUCT_BRIEF = """
PRODUCT: "30-Day Gentle Reset for Exhausted Moms" — a PDF guide by Alice (@MOTHER_INBALANCE)
BRAND: Mother in Balance
AESTHETIC: Warm beige/taupe, serif font, gold line illustrations, minimal, feminine, calm

CORE PAIN POINTS ADDRESSED:
- Overstimulation — nervous system always "on", never switching off
- Guilt around resting — feeling like rest must be earned
- Mental load / invisible work — being the manager of everything
- Feeling erased — losing identity in motherhood
- Waking up exhausted before the day starts
- Carrying everything alone, partner doesn't see the invisible work

UNIQUE POSITIONING (critical — this is the differentiator):
- Nervous system regulation framing — NOT hustle, discipline, or productivity
- "This is not weakness — it's a nervous system under continuous pressure"
- No perfect routines required. Designed for real, messy days.
- Each daily action takes 1–5 minutes, doable with child in the room
- Anti-"become a better mother" — explicitly about calming the woman, not improving the mom

PROOF POINT: "In less than a month, over 10,000 women found their way there"
AUTHOR VOICE: Warm, personal, first-person, non-judgmental. Signs off "love, Alice"
STRUCTURE: 4 weeks — nervous system → partnership load → self identity → integration

PLATFORM: Sold on beacons.ai
BUDGET CONTEXT: Small budget (<$100/mo) — ads need to punch hard with copy, not production value
"""

CAMPAIGN_SCHEMA = {
    "campaign_name": "short name (3-5 words)",
    "angle": "one sentence describing the psychological hook strategy",
    "primary_hook": "the scroll-stopping first line — max 10 words, no period",
    "body_copy": "3-5 sentences of ad body copy, warm tone, mirrors product voice",
    "cta_text": "call-to-action button text (max 5 words)",
    "visual_direction": "specific description of what the photo/video should show — real, not stock-photo perfect",
    "placement": "Feed | Stories | Reels | Feed + Stories",
    "audience_targeting": "age range, interests, behaviors to target in Meta Ads Manager",
    "budget_note": "how to use this in a <$100/mo budget context",
    "why_it_works": "1-2 sentences explaining the psychological reasoning"
}


def build_prompt(price: str, url: str, competitor_insights: dict) -> str:
    competitor_summary = json.dumps({
        "common_hooks": competitor_insights.get("common_hooks", []),
        "price_points_seen": competitor_insights.get("price_points_seen", []),
        "positioning_notes": competitor_insights.get("positioning_notes", []),
        "differentiation_opportunity": competitor_insights.get("differentiation_opportunity", ""),
    }, indent=2)

    return f"""You are a performance marketing specialist who runs Instagram and Facebook ads for women's wellness digital products. You understand female psychology, maternal exhaustion, and what makes someone stop scrolling and click.

{PRODUCT_BRIEF}

PRODUCT PRICE: ${price}
PURCHASE LINK: {url}

COMPETITOR INTELLIGENCE:
{competitor_summary}

Your task: Generate exactly 5 distinct ad campaigns for this product. Each campaign must have a different psychological angle — no two hooks can use the same emotional trigger.

CRITICAL RULES:
- Match the product's warm, gentle, non-judgmental tone — no aggressive urgency, no "LIMITED TIME"
- The nervous system angle is the biggest differentiator — use it prominently in at least 2 campaigns
- At least 1 campaign must use the "10,000 women" social proof
- At least 1 campaign must be designed for Reels (short-form video, text-card format)
- At least 1 campaign should use Alice's personal story voice
- Body copy should feel like it was written by a tired mom who found relief, not a marketer
- Never use words: hustle, grind, crush, game-changer, transform, life-changing

Return a JSON array of exactly 5 campaign objects. Each object must have these exact keys:
{json.dumps(list(CAMPAIGN_SCHEMA.keys()), indent=2)}

Return ONLY the JSON array. No markdown, no explanation, no preamble.
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--price", required=True, help="Product price as number, e.g. 17")
    parser.add_argument("--url", required=True, help="Full beacons.ai product URL")
    args = parser.parse_args()

    # Load competitor research if available
    try:
        competitor_insights = load_tmp("competitor_research.json")
        print("Loaded competitor research from .tmp/")
    except FileNotFoundError:
        print("No competitor research found — run research_competitors.py first for better results.")
        print("Proceeding with product analysis only...\n")
        competitor_insights = {}

    api_key = env("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_key)

    prompt = build_prompt(args.price, args.url, competitor_insights)

    print("Generating 5 ad campaigns with Claude...\n")
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    # Parse JSON response
    try:
        campaigns = json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract JSON array if Claude added any surrounding text
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start != -1 and end > start:
            campaigns = json.loads(raw[start:end])
        else:
            print("ERROR: Could not parse Claude's response as JSON.")
            print("Raw response saved to .tmp/campaigns_raw.txt")
            save_tmp("campaigns_raw.txt", raw)
            sys.exit(1)

    if len(campaigns) != 5:
        print(f"Warning: Expected 5 campaigns, got {len(campaigns)}")

    output = {
        "product_price": args.price,
        "product_url": args.url,
        "campaigns": campaigns,
    }

    save_tmp("campaigns.json", output)

    # Print preview
    print(f"\n{'='*60}")
    print(f"Generated {len(campaigns)} campaigns:")
    print(f"{'='*60}")
    for i, c in enumerate(campaigns, 1):
        print(f"\n[{i}] {c.get('campaign_name', 'N/A')}")
        print(f"    Hook: {c.get('primary_hook', '')}")
        print(f"    Placement: {c.get('placement', '')}")
        print(f"    Audience: {c.get('audience_targeting', '')}")

    print(f"\n{'='*60}")
    print("Next step: python tools/export_to_sheets.py")


if __name__ == "__main__":
    main()
