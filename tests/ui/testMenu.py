"""
tests/ui/testMenu.py — Select line and navigate to Production Overview
Production Overview opens in a NEW TAB — we capture it with page event.
"""

import os
import pytest
from pages.login_page import LoginPage
from pages.menuPage import MenuPage

USERNAME = os.getenv("TEST_USERNAME", "")
PASSWORD = os.getenv("TEST_PASSWORD", "")
COMPANY  = os.getenv("COMPANY", "BKT_1")
PLANT    = os.getenv("PLANT", "BKT_Plant")
LINE     = os.getenv("LINE", "GOTR_3_Line_Sanity_checks")
MODULE   = "Production Overview"


@pytest.mark.ui
@pytest.mark.smoke
def test_login_select_line_and_open_production_overview(page, base_url, context):
    """
    1. Login → Menu
    2. Select Company → Plant → Line
    3. Click Production Overview (opens in new tab)
    4. Switch to new tab and verify URL
    """

    # Step 1 — Login
    login = LoginPage(page, base_url).navigate()
    login.login(USERNAME, PASSWORD)
    page.wait_for_url("**/Menu/**", timeout=15_000)
    print(f"✓ Logged in — landed on: {page.url}")

    menu = MenuPage(page, base_url)

    # Step 2 — Select dropdowns
    menu.select_company(COMPANY)
    print(f"✓ Company selected: {COMPANY}")

    menu.select_plant(PLANT)
    print(f"✓ Plant selected: {PLANT}")

    menu.select_line(LINE)
    print(f"✓ Line selected: {LINE}")

    # Step 3 — Listen for new tab, then click module
    with context.expect_page() as new_page_info:
        page.get_by_text(MODULE, exact=True).click()
        print(f"✓ Clicked: {MODULE}")

    # Step 4 — Switch to new tab
    new_page = new_page_info.value
    new_page.wait_for_load_state("domcontentloaded", timeout=60_000)
    print(f"✓ New tab URL: {new_page.url}")

    assert "ProductionOverview" in new_page.url, \
        f"Expected ProductionOverview in URL, got: {new_page.url}"
    print("✓ Test passed!")