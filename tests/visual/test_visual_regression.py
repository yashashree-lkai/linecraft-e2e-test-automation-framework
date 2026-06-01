"""
tests/visual/test_visual_regression.py — Visual regression tests.

First run: baselines are captured automatically.
Subsequent runs: new screenshots are diffed against baselines.

To intentionally update a baseline:
    pytest tests/visual/ -k test_homepage --update-baselines
"""

import pytest
from utils.visual_helper import capture_and_compare


def pytest_addoption(parser):
    parser.addoption("--update-baselines", action="store_true", default=False,
                     help="Overwrite baseline screenshots instead of comparing.")


@pytest.fixture()
def update_baselines(request) -> bool:
    return request.config.getoption("--update-baselines", default=False)


@pytest.mark.visual
class TestVisualRegression:
    """Full-page and component-level visual snapshots."""

    def test_homepage_full_page(self, page, base_url, update_baselines):
        """Homepage full-page screenshot matches baseline."""
        page.goto(base_url)
        page.wait_for_load_state("networkidle")
        capture_and_compare(page, "homepage_full", update_baseline=update_baselines)

    def test_login_page(self, page, base_url, update_baselines):
        """Login page layout hasn't changed."""
        page.goto(f"{base_url}/login")
        page.wait_for_load_state("networkidle")
        capture_and_compare(page, "login_page", update_baseline=update_baselines)

    def test_login_form_component(self, page, base_url, update_baselines):
        """Only the login form component is compared (element screenshot)."""
        page.goto(f"{base_url}/login")
        page.wait_for_load_state("networkidle")
        capture_and_compare(
            page,
            "login_form_component",
            selector="[data-testid='login-form']",
            update_baseline=update_baselines,
        )

    def test_dashboard_after_login(self, authenticated_page, base_url, update_baselines):
        """Dashboard layout matches baseline after authentication."""
        authenticated_page.goto(f"{base_url}/dashboard")
        authenticated_page.wait_for_load_state("networkidle")
        capture_and_compare(
            authenticated_page,
            "dashboard_full",
            update_baseline=update_baselines,
        )

    def test_dashboard_nav_component(self, authenticated_page, base_url, update_baselines):
        """Navigation bar component visual check."""
        authenticated_page.goto(f"{base_url}/dashboard")
        capture_and_compare(
            authenticated_page,
            "dashboard_nav",
            selector="nav[data-testid='main-nav']",
            threshold=0.05,          # tighter threshold for nav
            update_baseline=update_baselines,
        )

    def test_responsive_mobile_viewport(self, context, base_url, update_baselines):
        """Homepage renders correctly on mobile (375px width)."""
        mobile_page = context.new_page()
        mobile_page.set_viewport_size({"width": 375, "height": 812})
        mobile_page.goto(base_url)
        mobile_page.wait_for_load_state("networkidle")
        capture_and_compare(
            mobile_page,
            "homepage_mobile_375",
            update_baseline=update_baselines,
        )
        mobile_page.close()
