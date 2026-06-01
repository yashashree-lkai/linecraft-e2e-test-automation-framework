"""
pages/dashboard_page.py — Example Page Object for the Dashboard.
Replace selectors with your app's real ones.
"""

from __future__ import annotations

from playwright.sync_api import Locator, expect
from pages.base_page import BasePage


class DashboardPage(BasePage):
    URL = "/dashboard"

    # ── Locators ──────────────────────────────────────────────────────────────

    @property
    def welcome_heading(self) -> Locator:
        return self.page.locator("h1[data-testid='welcome']")

    @property
    def nav_menu(self) -> Locator:
        return self.page.locator("nav[data-testid='main-nav']")

    @property
    def user_avatar(self) -> Locator:
        return self.page.locator("[data-testid='user-avatar']")

    @property
    def logout_button(self) -> Locator:
        return self.page.locator("[data-testid='logout']")

    @property
    def notification_badge(self) -> Locator:
        return self.page.locator("[data-testid='notification-badge']")

    # ── Actions ───────────────────────────────────────────────────────────────

    def logout(self) -> None:
        self.user_avatar.click()
        self.logout_button.click()
        self.page.wait_for_url("**/login", timeout=10_000)

    def navigate_to(self, section: str) -> "DashboardPage":
        """Click a nav item by its visible label."""
        self.nav_menu.get_by_text(section, exact=True).click()
        return self

    # ── Assertions ────────────────────────────────────────────────────────────

    def assert_logged_in(self, username: str | None = None) -> "DashboardPage":
        expect(self.welcome_heading).to_be_visible()
        if username:
            expect(self.welcome_heading).to_contain_text(username)
        return self

    def assert_notification_count(self, count: int) -> "DashboardPage":
        expect(self.notification_badge).to_have_text(str(count))
        return self
