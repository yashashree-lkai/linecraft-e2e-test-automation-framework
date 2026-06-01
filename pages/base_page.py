"""
pages/base_page.py — Every page object inherits from this.
Provides navigation, waiting helpers, and common assertions.
"""

from __future__ import annotations

import os
from pathlib import Path
from playwright.sync_api import Page, Locator, expect


class BasePage:
    """
    Foundation for all Page Objects.

    Usage:
        class LoginPage(BasePage):
            URL = "/login"

            @property
            def email_input(self) -> Locator:
                return self.page.locator("[data-testid='email']")
    """

    # Subclasses set this to their relative path, e.g. "/login"
    URL: str = "/"

    def __init__(self, page: Page, base_url: str | None = None) -> None:
        self.page = page
        self.base_url = base_url or os.getenv("BASE_URL", "https://your-app.com")

    # ── Navigation ────────────────────────────────────────────────────────────

    def navigate(self, path: str | None = None) -> "BasePage":
        """Go to this page's URL (or an explicit path)."""
        url = self.base_url.rstrip("/") + (path or self.URL)
        self.page.goto(url)
        return self

    def reload(self) -> "BasePage":
        self.page.reload()
        return self

    def go_back(self) -> "BasePage":
        self.page.go_back()
        return self

    # ── Waiting helpers ───────────────────────────────────────────────────────

    def wait_for_load(self, state: str = "networkidle") -> "BasePage":
        self.page.wait_for_load_state(state)
        return self

    def wait_for_selector(self, selector: str, timeout: int = 10_000) -> Locator:
        self.page.wait_for_selector(selector, timeout=timeout)
        return self.page.locator(selector)

    def wait_for_url(self, pattern: str, timeout: int = 15_000) -> "BasePage":
        self.page.wait_for_url(pattern, timeout=timeout)
        return self

    # ── Interaction helpers ───────────────────────────────────────────────────

    def fill(self, selector: str, value: str) -> "BasePage":
        self.page.fill(selector, value)
        return self

    def click(self, selector: str) -> "BasePage":
        self.page.click(selector)
        return self

    def select_option(self, selector: str, value: str) -> "BasePage":
        self.page.select_option(selector, value)
        return self

    def clear_and_fill(self, selector: str, value: str) -> "BasePage":
        self.page.locator(selector).clear()
        self.page.fill(selector, value)
        return self

    # ── Query helpers ─────────────────────────────────────────────────────────

    def get_text(self, selector: str) -> str:
        return self.page.locator(selector).inner_text()

    def is_visible(self, selector: str) -> bool:
        return self.page.locator(selector).is_visible()

    def count(self, selector: str) -> int:
        return self.page.locator(selector).count()

    # ── Assertion shortcuts ───────────────────────────────────────────────────

    def assert_url_contains(self, fragment: str) -> "BasePage":
        expect(self.page).to_have_url(lambda u: fragment in u)
        return self

    def assert_title(self, title: str) -> "BasePage":
        expect(self.page).to_have_title(title)
        return self

    def assert_visible(self, selector: str) -> "BasePage":
        expect(self.page.locator(selector)).to_be_visible()
        return self

    def assert_text(self, selector: str, text: str) -> "BasePage":
        expect(self.page.locator(selector)).to_have_text(text)
        return self

    # ── Screenshot ────────────────────────────────────────────────────────────

    def screenshot(self, name: str, full_page: bool = True) -> Path:
        out = Path("screenshots") / f"{name}.png"
        self.page.screenshot(path=str(out), full_page=full_page)
        return out
