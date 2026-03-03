"""
Step 1: Competitor Research
Searches Serper for similar mom wellness digital products, ad hooks, and pricing.
Usage: python tools/research_competitors.py
Output: .tmp/competitor_research.json
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
from _base import env, save_tmp

QUERIES = [
    '"exhausted moms" digital product instagram',
    '"mom burnout" ebook reset guide',
    '"mental load" "moms" pdf guide wellness',
    '"nervous system" "mothers" "reset" digital download',
    'site:beacons.ai "moms" "reset" OR "burnout" OR "exhausted"',
    'site:gumroad.com "exhausted mom" OR "mom burnout" guide',
    'instagram "motherhood burnout" self care guide pdf',
    '#mommentalhealth #momwellness "digital download" OR "pdf guide"',
]

def serper_search(query: str, api_key: str) -> list[dict]:
    resp = requests.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
        json={"q": query, "num": 5},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    results = []
    for item in data.get("organic", []):
        results.append({
            "title": item.get("title", ""),
            "link": item.get("link", ""),
            "snippet": item.get("snippet", ""),
        })
    return results


def extract_insights(all_results: list[dict]) -> dict:
    """
    Pull out key competitive intelligence from raw search results.
    Returns structured insights for the campaign generator.
    """
    hooks_seen = []
    products_found = []
    price_mentions = []
    positioning_notes = []

    for r in all_results:
        snippet = r.get("snippet", "").lower()
        title = r.get("title", "")
        link = r.get("link", "")

        # Detect hooks / value props
        for phrase in ["no perfection", "no discipline", "5 minutes", "nervous system",
                       "burnout", "mental load", "overwhelm", "exhausted", "survival mode",
                       "self-care", "reset", "gentle", "real life"]:
            if phrase in snippet:
                hooks_seen.append(phrase)

        # Detect price points
        for price in ["$5", "$7", "$9", "$12", "$15", "$17", "$19", "$27", "$37", "$47"]:
            if price in snippet or price in title:
                price_mentions.append(price)

        if any(kw in link for kw in ["gumroad", "beacons", "etsy", "stan.store", "ko-fi"]):
            products_found.append({"title": title, "link": link, "snippet": r.get("snippet", "")})

        # Note positioning
        if "perfect" in snippet and ("no" in snippet or "don't" in snippet):
            positioning_notes.append("Anti-perfection messaging common in this niche")
        if "busy mom" in snippet or "tired mom" in snippet:
            positioning_notes.append("'Busy/tired mom' framing used by competitors")

    return {
        "products_found": products_found[:10],
        "common_hooks": list(set(hooks_seen)),
        "price_points_seen": list(set(price_mentions)),
        "positioning_notes": list(set(positioning_notes)),
        "differentiation_opportunity": (
            "Most competitors use generic 'self-care' framing. "
            "The nervous system / 'not weakness, it's an overloaded system' angle "
            "is more specific and credible — lean into this hard."
        ),
    }


def main():
    api_key = env("SERPER_API_KEY")
    print("Searching for competitors across 8 queries...\n")

    all_results = []
    for i, query in enumerate(QUERIES, 1):
        print(f"  [{i}/{len(QUERIES)}] {query}")
        try:
            results = serper_search(query, api_key)
            all_results.extend(results)
        except requests.HTTPError as e:
            print(f"    Warning: query failed — {e}")

    print(f"\nTotal results collected: {len(all_results)}")

    insights = extract_insights(all_results)
    insights["raw_results"] = all_results

    save_tmp("competitor_research.json", insights)
    print("\nDone. Next step: python tools/generate_ad_campaigns.py --price 17 --url YOUR_BEACONS_URL")


if __name__ == "__main__":
    main()
