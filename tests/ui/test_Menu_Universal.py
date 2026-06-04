"""
tests/ui/test_menu_universal.py

Universal test that works on ANY environment.
Waits for actual Menu page element instead of 'load' event.
"""

import pytest
from pages.login_page import LoginPage
from pages.menuPage import MenuPage

MODULE = "Production Overview"


@pytest.mark.ui
@pytest.mark.smoke
@pytest.mark.critical
def test_login_and_select_line_universal(page, context, base_url, test_data, environment):
    """
    Universal Menu Selection Test
    """

    username = test_data["username"]
    password = test_data["password"]
    company  = test_data["company"]
    plant    = test_data["plant"]
    line     = test_data["line"]

    print(f"\n{'='*70}")
    print(f"🌍 TEST ENVIRONMENT: {environment.upper()}")
    print(f"👤 USERNAME: {username}")
    print(f"📍 SELECTIONS: Company={company}, Plant={plant}, Line={line}")
    print(f"{'='*70}\n")

    # ── Step 1: Login ────────────────────────────────────────────────
    print("📝 Step 1: Login")
    login = LoginPage(page, base_url).navigate()
    login.login(username, password)

    # Instead of waiting for 'load' event (which hangs),
    # wait for the URL to contain '/Menu'
    print("⏳ Waiting for Menu page to load...")
    page.wait_for_url("**Menu**", timeout=20_000)
    print(f"✓ URL changed to Menu page\n")

    # ── Step 2: Wait for Menu page elements to be ready ──────────────
    print("⏳ Step 2: Waiting for Menu elements to load...")
    page.wait_for_timeout(2000)  # Give page time to render

    try:
        # Wait for a Menu page element - "Line Selection" heading
        page.locator("text=Line Selection").wait_for(state="visible", timeout=10_000)
        print(f"✓ Menu page elements loaded\n")
    except:
        print(f"⚠️  'Line Selection' not found, but continuing...\n")

    # ── Step 3: Wait for dropdowns to be ready ──────────────────────
    print("⏳ Step 3: Waiting for dropdown buttons...")
    page.locator("button[class*='dropdownButtonStyle']").first.wait_for(
        state="attached", timeout=10_000
    )
    print(f"✓ Dropdown buttons ready\n")

    # ── Step 4: Menu Selection ──────────────────────────────────────
    print("📋 Step 4: Menu Selection")
    menu = MenuPage(page, base_url)

    print(f"Selecting company: {company}")
    menu.select_company(company)
    print(f"✓ Company selected: {company}")

    print(f"Selecting plant: {plant}")
    menu.select_plant(plant)
    print(f"✓ Plant selected: {plant}")

    print(f"Selecting line: {line}")
    menu.select_line(line)
    print(f"✓ Line selected: {line}\n")

    # ── Step 5: Navigate to Module ──────────────────────────────────
    print("🚀 Step 5: Navigate to Module")
    with context.expect_page() as new_page_info:
        page.get_by_text(MODULE, exact=True).click()

    new_page = new_page_info.value
    new_page.wait_for_url("**ProductionOverview**", timeout=10_000)
    print(f"✓ Navigated to: {MODULE}\n")

    # ── Assertions ──────────────────────────────────────────────────
    assert "ProductionOverview" in new_page.url

    print(f"{'='*70}")
    print(f"✅ TEST PASSED on {environment.upper()}")
    print(f"{'='*70}\n")