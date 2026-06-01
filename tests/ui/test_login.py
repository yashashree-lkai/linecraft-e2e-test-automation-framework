"""
tests/ui/test_login.py — Login test for linecraft.ai
"""

import os
import pytest
from pages.login_page import LoginPage

USERNAME = os.getenv("TEST_USERNAME", "")
PASSWORD = os.getenv("TEST_PASSWORD", "")


@pytest.mark.ui
@pytest.mark.smoke
def test_successful_login(page, base_url):
    """Login with valid credentials and land on the next page."""
    login = LoginPage(page, base_url).navigate()
    login.login(USERNAME, PASSWORD)
    page.wait_for_url(lambda url: "signin" not in url, timeout=15_000)
    print(f"Landed on: {page.url}")