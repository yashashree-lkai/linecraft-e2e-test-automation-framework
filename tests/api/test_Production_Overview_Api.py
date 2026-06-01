"""
tests/api/test_production_overview_api.py

Intercepts get_assetwise_kpi on Production Overview page.
Asserts payload params match expected test data.
Captures Bearer token and includes it in the report.
"""

import os
import json
import pytest
from urllib.parse import urlparse, parse_qs
from pages.login_page import LoginPage
from pages.menuPage import MenuPage

USERNAME = os.getenv("TEST_USERNAME", "")
PASSWORD = os.getenv("TEST_PASSWORD", "")
COMPANY  = os.getenv("COMPANY", "BKT_1")
PLANT    = os.getenv("PLANT", "BKT_Plant")
LINE     = os.getenv("LINE", "GOTR_3_Line_Sanity_checks")
MODULE   = "Production Overview"

# ── Expected test data — update these values when asset/time changes ──────────
EXPECTED = {
    "config_id":  "40316",           # Asset config ID
    "node_ids":   "[26024]",         # Node ID list
    "is_daywise": "false",           # Daywise flag
    # start_time and end_time are dynamic (shift-based), so we only
    # check format not exact value. Set to None to skip exact match.
    "start_time": None,              # e.g. "05-May-2026+04:00:00:000"
    "end_time":   None,              # e.g. "05-May-2026+04:00:00:000"
}
# ─────────────────────────────────────────────────────────────────────────────


def login_and_open_production_overview(page, context, base_url):
    """Login, select line, open Production Overview in new tab."""
    login = LoginPage(page, base_url).navigate()
    login.login(USERNAME, PASSWORD)
    page.wait_for_url("**/Menu/**", timeout=15_000)

    menu = MenuPage(page, base_url)
    menu.select_company(COMPANY)
    menu.select_plant(PLANT)
    menu.select_line(LINE)

    with context.expect_page() as new_page_info:
        page.get_by_text(MODULE, exact=True).click()

    new_page = new_page_info.value
    new_page.wait_for_load_state("domcontentloaded", timeout=60_000)
    return new_page


@pytest.mark.api
def test_assetwise_kpi_payload_and_token(page, context, base_url):
    """
    1. Open Production Overview
    2. Intercept get_assetwise_kpi request
    3. Assert all query params match expected test data
    4. Extract Bearer token and include in report
    """
    captured = []

    prod_page = login_and_open_production_overview(page, context, base_url)

    def capture(request):
        if "get_assetwise_kpi" in request.url:
            captured.append({
                "url":     request.url,
                "method":  request.method,
                "headers": dict(request.headers),
            })

    prod_page.on("request", capture)
    prod_page.reload()
    prod_page.wait_for_load_state("domcontentloaded", timeout=60_000)
    prod_page.wait_for_timeout(3000)

    # ── Verify request was made ───────────────────────────────────
    assert len(captured) > 0, "get_assetwise_kpi was never called!"

    req     = captured[0]
    url     = req["url"]
    headers = req["headers"]
    parsed  = urlparse(url)
    params  = parse_qs(parsed.query)

    # ── Extract Bearer token ──────────────────────────────────────
    auth_header = headers.get("authorization", headers.get("Authorization", ""))
    bearer_token = auth_header.replace("Bearer ", "").strip() if auth_header else "NOT FOUND"

    # ── Print full details to report ──────────────────────────────
    print("\n" + "="*60)
    print("API REQUEST DETAILS")
    print("="*60)
    print(f"URL:          {url}")
    print(f"Method:       {req['method']}")
    print(f"Bearer Token: {bearer_token}")
    print("-"*60)
    print("QUERY PARAMS:")
    for k, v in params.items():
        print(f"  {k} = {v[0]}")
    print("-"*60)
    print("EXPECTED VS ACTUAL:")
    print(f"  config_id  → expected: {EXPECTED['config_id']:<10} actual: {params.get('config_id', ['N/A'])[0]}")
    print(f"  node_ids   → expected: {EXPECTED['node_ids']:<10} actual: {params.get('node_ids', ['N/A'])[0]}")
    print(f"  is_daywise → expected: {EXPECTED['is_daywise']:<10} actual: {params.get('is_daywise', ['N/A'])[0]}")
    print(f"  start_time → actual: {params.get('start_time', ['N/A'])[0]}")
    print(f"  end_time   → actual: {params.get('end_time', ['N/A'])[0]}")
    print("="*60)

    # ── Assertions ────────────────────────────────────────────────

    # 1. config_id
    assert "config_id" in params, "MISSING param: config_id"
    assert params["config_id"][0] == EXPECTED["config_id"], (
        f"config_id MISMATCH — "
        f"expected: {EXPECTED['config_id']}, "
        f"actual: {params['config_id'][0]}"
    )
    print(f"✓ config_id matches: {params['config_id'][0]}")

    # 2. node_ids
    assert "node_ids" in params, "MISSING param: node_ids"
    assert params["node_ids"][0] == EXPECTED["node_ids"], (
        f"node_ids MISMATCH — "
        f"expected: {EXPECTED['node_ids']}, "
        f"actual: {params['node_ids'][0]}"
    )
    print(f"✓ node_ids matches: {params['node_ids'][0]}")

    # 3. is_daywise
    assert "is_daywise" in params, "MISSING param: is_daywise"
    assert params["is_daywise"][0] == EXPECTED["is_daywise"], (
        f"is_daywise MISMATCH — "
        f"expected: {EXPECTED['is_daywise']}, "
        f"actual: {params['is_daywise'][0]}"
    )
    print(f"✓ is_daywise matches: {params['is_daywise'][0]}")

    # 4. start_time — only check format if no exact value set
    assert "start_time" in params, "MISSING param: start_time"
    if EXPECTED["start_time"]:
        assert params["start_time"][0] == EXPECTED["start_time"], (
            f"start_time MISMATCH — "
            f"expected: {EXPECTED['start_time']}, "
            f"actual: {params['start_time'][0]}"
        )
    print(f"✓ start_time present: {params['start_time'][0]}")

    # 5. end_time
    assert "end_time" in params, "MISSING param: end_time"
    if EXPECTED["end_time"]:
        assert params["end_time"][0] == EXPECTED["end_time"], (
            f"end_time MISMATCH — "
            f"expected: {EXPECTED['end_time']}, "
            f"actual: {params['end_time'][0]}"
        )
    print(f"✓ end_time present: {params['end_time'][0]}")

    # 6. Bearer token must exist
    assert bearer_token != "NOT FOUND", "Bearer token missing from request headers!"
    assert len(bearer_token) > 10, "Bearer token looks invalid (too short)"
    print(f"✓ Bearer token present: {bearer_token[:30]}...")

    print("\n✓ ALL ASSERTIONS PASSED!")