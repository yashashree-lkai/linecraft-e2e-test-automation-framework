"""
pages/menu_page.py — Main Menu page (wks1103/Menu/)
React Select requires mousedown on the option div, not the label inside it.
"""

from __future__ import annotations
from playwright.sync_api import Locator, expect
from pages.base_page import BasePage


class MenuPage(BasePage):
    URL = "/Menu/"

    @property
    def company_dropdown_btn(self) -> Locator:
        return self.page.locator("div.drop-title:has-text('Company Name') ~ div button").first

    @property
    def plant_dropdown_btn(self) -> Locator:
        return self.page.locator("div.drop-title:has-text('Plant Name') ~ div button").first

    @property
    def line_dropdown_btn(self) -> Locator:
        return self.page.locator("div.drop-title:has-text('Line Name') ~ div button").first

    def _select_dropdown_option(self, btn: Locator, value: str) -> None:
        """
        Open React Select dropdown, scroll to option, fire mousedown
        on the select__option container (React Select listens here).
        """
        btn.click()
        self.page.wait_for_timeout(600)

        self.page.locator("div.select__menu-list").first.wait_for(
            state="visible", timeout=5_000
        )

        # Scroll and fire mousedown on select__option (React Select's click target)
        self.page.evaluate(f"""
            () => {{
                const menuList = document.querySelector('div.select__menu-list');
                if (!menuList) return;

                for (let scrollTop of [0, 100, 200, 300, 400, 500, 600, 700, 800]) {{
                    menuList.scrollTop = scrollTop;

                    // React Select uses div[class*="option"] as the clickable row
                    const options = Array.from(menuList.querySelectorAll('[class*="option"]'));
                    const target = options.find(el => el.textContent.trim() === '{value}');

                    if (target) {{
                        // React Select selects on mousedown
                        target.dispatchEvent(new MouseEvent('mousedown', {{
                            bubbles: true, cancelable: true, view: window
                        }}));
                        target.dispatchEvent(new MouseEvent('mouseup', {{
                            bubbles: true, cancelable: true, view: window
                        }}));
                        target.dispatchEvent(new MouseEvent('click', {{
                            bubbles: true, cancelable: true, view: window
                        }}));
                        return;
                    }}
                }}
            }}
        """)
        self.page.wait_for_timeout(600)

        # Close if still open
        if self.page.locator("div.select__menu-list").is_visible():
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(300)

        self.page.locator("div.select__menu-list").wait_for(
            state="hidden", timeout=5_000
        )
        self.page.wait_for_timeout(400)

    def select_company(self, value: str) -> "MenuPage":
        self._select_dropdown_option(self.company_dropdown_btn, value)
        return self

    def select_plant(self, value: str) -> "MenuPage":
        self._select_dropdown_option(self.plant_dropdown_btn, value)
        return self

    def select_line(self, value: str) -> "MenuPage":
        self._select_dropdown_option(self.line_dropdown_btn, value)
        return self

    def select_module(self, module_name: str) -> None:
        self.page.get_by_text(module_name, exact=True).click()
        self.page.wait_for_load_state("networkidle", timeout=15_000)

    def assert_on_menu_page(self) -> "MenuPage":
        expect(self.page).to_have_url(lambda u: "Menu" in u)
        return self