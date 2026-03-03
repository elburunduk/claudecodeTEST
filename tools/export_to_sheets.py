"""
Step 3: Export to Google Sheets
Writes campaigns and competitor research to a Google Sheet (two tabs).
Usage: python tools/export_to_sheets.py
Output: Prints the Google Sheet URL

Requires:
  - credentials.json in project root (download from Google Cloud Console)
  - GOOGLE_SHEET_ID in .env
  - pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from _base import env, load_tmp, ROOT

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
TOKEN_PATH = ROOT / "token.json"
CREDS_PATH = ROOT / "credentials.json"


def get_sheets_service():
    creds = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDS_PATH.exists():
                raise FileNotFoundError(
                    "credentials.json not found in project root.\n"
                    "Download it from: Google Cloud Console → APIs & Services → Credentials → OAuth 2.0 Client IDs"
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)

        TOKEN_PATH.write_text(creds.to_json())

    return build("sheets", "v4", credentials=creds)


def clear_and_write(service, sheet_id: str, tab_name: str, rows: list[list]):
    """Clear a tab and write rows to it. Creates tab if it doesn't exist."""
    spreadsheet = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    existing_tabs = [s["properties"]["title"] for s in spreadsheet.get("sheets", [])]

    if tab_name not in existing_tabs:
        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body={"requests": [{"addSheet": {"properties": {"title": tab_name}}}]},
        ).execute()
        print(f"  Created tab: {tab_name}")

    range_name = f"'{tab_name}'!A1"
    service.spreadsheets().values().clear(
        spreadsheetId=sheet_id, range=range_name
    ).execute()

    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption="RAW",
        body={"values": rows},
    ).execute()
    print(f"  Wrote {len(rows)-1} rows to tab: {tab_name}")


def build_campaigns_tab(data: dict) -> list[list]:
    campaigns = data.get("campaigns", [])
    price = data.get("product_price", "")
    url = data.get("product_url", "")

    headers = [
        "#", "Campaign Name", "Angle", "Primary Hook", "Body Copy",
        "CTA Text", "Visual Direction", "Placement", "Audience Targeting",
        "Budget Note", "Why It Works", "Price", "Product URL"
    ]

    rows = [headers]
    for i, c in enumerate(campaigns, 1):
        rows.append([
            i,
            c.get("campaign_name", ""),
            c.get("angle", ""),
            c.get("primary_hook", ""),
            c.get("body_copy", ""),
            c.get("cta_text", ""),
            c.get("visual_direction", ""),
            c.get("placement", ""),
            c.get("audience_targeting", ""),
            c.get("budget_note", ""),
            c.get("why_it_works", ""),
            f"${price}",
            url,
        ])
    return rows


def build_competitor_tab(data: dict) -> list[list]:
    headers = ["Type", "Detail"]
    rows = [headers]

    rows.append(["=== DIFFERENTIATION OPPORTUNITY ===", ""])
    rows.append(["Insight", data.get("differentiation_opportunity", "")])
    rows.append(["", ""])

    rows.append(["=== COMMON HOOKS IN MARKET ===", ""])
    for hook in data.get("common_hooks", []):
        rows.append(["Hook keyword", hook])
    rows.append(["", ""])

    rows.append(["=== PRICE POINTS SEEN ===", ""])
    for price in data.get("price_points_seen", []):
        rows.append(["Price point", price])
    rows.append(["", ""])

    rows.append(["=== POSITIONING NOTES ===", ""])
    for note in data.get("positioning_notes", []):
        rows.append(["Note", note])
    rows.append(["", ""])

    rows.append(["=== PRODUCTS FOUND ===", ""])
    for p in data.get("products_found", []):
        rows.append([p.get("title", ""), p.get("link", "")])
        if p.get("snippet"):
            rows.append(["  snippet", p["snippet"]])

    return rows


def main():
    sheet_id = env("GOOGLE_SHEET_ID")

    # Load data
    campaigns_data = load_tmp("campaigns.json")
    try:
        competitor_data = load_tmp("competitor_research.json")
    except FileNotFoundError:
        print("Warning: No competitor research found. Run research_competitors.py first.")
        competitor_data = {}

    print("Authenticating with Google Sheets...")
    service = get_sheets_service()

    print("\nWriting to Google Sheet...")
    clear_and_write(service, sheet_id, "Campaigns", build_campaigns_tab(campaigns_data))
    clear_and_write(service, sheet_id, "Competitor Intel", build_competitor_tab(competitor_data))

    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
    print(f"\nDone! Open your sheet:")
    print(f"  {sheet_url}")
    print("\nShare this link with anyone who needs to review the campaigns.")


if __name__ == "__main__":
    main()
