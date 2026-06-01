"""
pages/login_page.py — Login page for linecraft.ai (wks1103/signin/)
"""

from __future__ import annotations
from playwright.sync_api import Locator, expect
from pages.base_page import BasePage


class LoginPage(BasePage):
    URL = "/"   # base_url already ends with /signin/

    @property
    def email_input(self) -> Locator:
        # Targets the Email Address field by its input type
        return self.page.get_by_placeholder("Email Address")

    @property
    def password_input(self) -> Locator:
        return self.page.get_by_placeholder("Password")

    @property
    def submit_button(self) -> Locator:
        # Targets the teal "Log In" button by its text
        return self.page.get_by_role("button", name="Log In")

    @property
    def error_message(self) -> Locator:
        # Update this selector after inspecting actual error element
        return self.page.locator(".error-message, [class*='error'], [class*='alert']").first

    def login(self, email: str, password: str) -> "LoginPage":
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.submit_button.click()
        return self

    def assert_error_visible(self) -> "LoginPage":
        expect(self.error_message).to_be_visible(timeout=5_000)
        return self

    def assert_on_login_page(self) -> "LoginPage":
        expect(self.page).to_have_url(lambda u: "signin" in u)
        return self