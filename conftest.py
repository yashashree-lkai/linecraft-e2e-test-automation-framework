"""
conftest.py — Central Playwright + pytest fixture hub.
All shared fixtures live here; test files just declare what they need.
"""

from __future__ import annotations

import os
import pytest
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import Browser, BrowserContext, Page

# ── Load .env ─────────────────────────────────────────────────────────────────
load_dotenv()

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
SCREENSHOTS_DIR = ROOT / "screenshots"
BASELINE_DIR = SCREENSHOTS_DIR / "baseline"
REPORTS_DIR = ROOT / "reports"

for d in (SCREENSHOTS_DIR, BASELINE_DIR, REPORTS_DIR):
    d.mkdir(parents=True, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# pytest hooks
# ══════════════════════════════════════════════════════════════════════════════

def pytest_addoption(parser: pytest.Parser) -> None:
    """Only add options NOT already registered by pytest-playwright."""
    parser.addoption("--browser-type", default=os.getenv("BROWSER", "chromium"),
                     choices=["chromium", "firefox", "webkit"])
    parser.addoption("--slow-mo", type=int, default=int(os.getenv("SLOW_MO", "0")))


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "ui: browser UI tests")
    config.addinivalue_line("markers", "api: API tests without a browser")
    config.addinivalue_line("markers", "visual: visual regression tests")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach a screenshot to the HTML report on failure."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page: Page | None = item.funcargs.get("page")
        if page and os.getenv("SCREENSHOT_ON_FAILURE", "true").lower() == "true":
            shot_path = SCREENSHOTS_DIR / f"FAIL_{item.name}.png"
            page.screenshot(path=str(shot_path), full_page=True)
            if hasattr(item, "extras"):
                from pytest_html import extras as html_extras
                item.extras.append(html_extras.image(str(shot_path)))


# ══════════════════════════════════════════════════════════════════════════════
# Config fixtures
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def browser_type_name(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--browser-type")


@pytest.fixture(scope="session")
def is_headless() -> bool:
    return os.getenv("HEADLESS", "true").lower() == "true"


@pytest.fixture(scope="session")
def slow_mo(request: pytest.FixtureRequest) -> int:
    return request.config.getoption("--slow-mo")


@pytest.fixture(scope="session")
def base_url(request: pytest.FixtureRequest) -> str:
    """
    pytest-playwright already registers --base-url.
    We read it here; falls back to .env BASE_URL.
    """
    val = request.config.getoption("--base-url", default=None)
    return val or os.getenv("BASE_URL", "https://your-app.com")


# ══════════════════════════════════════════════════════════════════════════════
# Context / Page fixtures  (function-scoped — fresh context per test)
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture()
def context(browser: Browser) -> BrowserContext:
    """Fresh browser context per test."""
    ctx = browser.new_context(
        viewport={
            "width": int(os.getenv("VIEWPORT_WIDTH", "1280")),
            "height": int(os.getenv("VIEWPORT_HEIGHT", "720")),
        },
    )
    ctx.set_default_timeout(int(os.getenv("DEFAULT_TIMEOUT", "30000")))
    ctx.set_default_navigation_timeout(int(os.getenv("NAVIGATION_TIMEOUT", "60000")))
    yield ctx
    ctx.close()


@pytest.fixture()
def page(context: BrowserContext) -> Page:
    """One page per test, inside its own context."""
    p = context.new_page()
    yield p
    p.close()


@pytest.fixture()
def authenticated_page(page: Page, base_url: str) -> Page:
    """
    Page that is already logged in.
    Replace the body with your real login flow.
    """
    page.goto(f"{base_url}/login")
    page.fill("[data-testid='email']", os.getenv("TEST_USERNAME", ""))
    page.fill("[data-testid='password']", os.getenv("TEST_PASSWORD", ""))
    page.click("[data-testid='login-btn']")
    page.wait_for_url(f"{base_url}/dashboard", timeout=15_000)
    return page


# ══════════════════════════════════════════════════════════════════════════════
# API fixture
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture()
def api_client():
    """requests.Session wrapper pre-configured with API base URL."""
    from utils.api_client import ApiClient
    client = ApiClient(
        base_url=os.getenv("API_BASE_URL", "https://api.your-app.com"),
        username=os.getenv("TEST_USERNAME", ""),
        password=os.getenv("TEST_PASSWORD", ""),
    )
    yield client
    client.close()