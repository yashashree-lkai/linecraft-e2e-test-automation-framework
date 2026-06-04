"""
pages/menu_page.py — Hybrid approach: Click if visible, Keyboard fallback for production
"""

from __future__ import annotations
from playwright.sync_api import Locator, expect
from pages.base_page import BasePage


class MenuPage(BasePage):
    URL = "/Menu/"

    def _get_dropdown_button(self, label_index: int) -> Locator:
        """Get dropdown button by index (0=company, 1=plant, 2=line)"""
        return self.page.locator("button[class*='dropdownButtonStyle']").nth(label_index)

    def _select_dropdown_option(self, btn: Locator, value: str) -> None:
        """Select option using a robust coordinate-free locator strategy"""

        # 1. Focus and click the dropdown button to guarantee menu expansion
        btn.focus()
        btn.click()
        self.page.wait_for_timeout(400) # Give the portal overlay time to render

        # 2. Strategy A: Try clicking via strict relative positioning
        # We look globally for the option text. If multiple exist, we use a loop
        # to try to find the one that responds to a native click.
        options = self.page.get_by_text(value, exact=True)
        count = options.count()

        success = False
        for i in range(count):
            try:
                opt = options.nth(i)
                if opt.is_visible():
                    opt.click(force=True, timeout=1000)
                    success = True
                    break
            except:
                continue

        # 3. Strategy B: KEYBOARD FALLBACK (The Production Lifesaver)
        # If the click didn't register or could not find a visible text element,
        # use keyboard navigation down the list item options.
        if not success:
            # Type into the focused dropdown container to jump straight to the option text,
            # or use standard keyboard navigation sequences.
            # Wait 2 seconds for page to settle
            self.page.wait_for_timeout(2000)

            # Wait for dropdown buttons to be present
            self.page.locator("button[class*='dropdownButtonStyle']").first.wait_for(
                state="attached", timeout=10_000
            )

            self.page.keyboard.press("ArrowDown")
            self.page.wait_for_timeout(100)

            # Type the target string to auto-focus the selection via built-in select matching
            self.page.keyboard.type(value, delay=50)
            self.page.wait_for_timeout(200)

            # Press Enter to finalize selection confirmation
            self.page.keyboard.press("Enter")

        # 4. Cleanup safety delay to give production a moment to refresh the page layout
        self.page.wait_for_timeout(500)

    def select_company(self, value: str) -> "MenuPage":
        btn = self._get_dropdown_button(0)
        self._select_dropdown_option(btn, value)
        return self

    def select_plant(self, value: str) -> "MenuPage":
        btn = self._get_dropdown_button(1)
        self._select_dropdown_option(btn, value)
        return self

    def select_line(self, value: str) -> "MenuPage":
        btn = self._get_dropdown_button(2)
        self._select_dropdown_option(btn, value)
        return self

    def select_module(self, module_name: str) -> None:
        self.page.get_by_text(module_name, exact=True).click()

    def assert_on_menu_page(self) -> "MenuPage":
        expect(self.page).to_have_url(lambda u: "Menu" in u)
        return self