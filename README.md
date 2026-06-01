# Playwright Python Test Framework

A production-ready test automation framework for web applications built with
**Playwright + pytest**. Supports UI testing, API testing, visual regression,
and CI/CD via GitHub Actions.

---

## Project Structure

```
playwright_framework/
├── conftest.py                  # Global fixtures (browser, page, auth, api_client)
├── pytest.ini                   # pytest config, markers, default options
├── requirements.txt
├── .env.example                 # Copy → .env and fill in your values
│
├── pages/                       # Page Object Model
│   ├── base_page.py             # Base class (navigate, fill, assert helpers)
│   ├── login_page.py            # Example: Login POM
│   └── dashboard_page.py        # Example: Dashboard POM
│
├── utils/
│   ├── api_client.py            # requests.Session wrapper with assertion helpers
│   ├── visual_helper.py         # Pixel-diff visual regression engine (Pillow)
│   └── helpers.py               # Random data generators, retry, date utils
│
├── tests/
│   ├── ui/
│   │   └── test_login.py        # Example UI test suite
│   ├── api/
│   │   └── test_users_api.py    # Example API test suite
│   └── visual/
│       └── test_visual_regression.py
│
├── screenshots/
│   ├── baseline/                # Reference images (commit these to git)
│   ├── actual/                  # Current-run captures
│   └── diff/                    # Side-by-side diff composites on failure
│
├── reports/                     # HTML reports (git-ignored)
│
└── .github/
    └── workflows/
        └── playwright.yml       # CI: API, UI (3 browsers), smoke, visual
```

---

## Quick Start

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install                 # Download browser binaries
```

### 2. Configure your environment

```bash
cp .env.example .env
# Edit .env — set BASE_URL, API_BASE_URL, TEST_USERNAME, TEST_PASSWORD
```

### 3. Run tests

```bash
# All tests
pytest

# Only UI tests, headed (watch the browser)
pytest -m ui --headless=false

# Only API tests
pytest -m api

# Only visual tests
pytest -m visual

# Smoke tests (fast subset)
pytest -m smoke

# Firefox only
pytest --browser-type=firefox

# Parallel (4 workers)
pytest -n 4
```

---

## Running Visual Tests

```bash
# First run — captures baselines automatically
pytest tests/visual/

# Compare against baselines
pytest tests/visual/

# Update baselines (after intentional UI changes)
pytest tests/visual/ --update-baselines
```

Baseline images live in `screenshots/baseline/`. **Commit them to git** so
the CI pipeline can download them as artifacts.

---

## Writing Tests

### UI Test (Page Object)

```python
import pytest
from pages.login_page import LoginPage

@pytest.mark.ui
@pytest.mark.smoke
def test_login_success(page, base_url):
    login = LoginPage(page, base_url).navigate()
    login.login("user@example.com", "Password1!")
    assert "/dashboard" in page.url
```

### API Test

```python
import pytest

@pytest.mark.api
def test_get_profile(api_client):
    resp = api_client.get("/users/me")
    api_client.assert_status(resp, 200)
    api_client.assert_schema(resp, ["id", "email", "name"])
```

### Adding a New Page Object

```python
# pages/my_page.py
from pages.base_page import BasePage
from playwright.sync_api import Locator

class MyPage(BasePage):
    URL = "/my-section"

    @property
    def some_button(self) -> Locator:
        return self.page.locator("[data-testid='my-btn']")

    def do_action(self) -> "MyPage":
        self.some_button.click()
        return self
```

---

## Markers

| Marker       | Purpose                              |
|--------------|--------------------------------------|
| `ui`         | Browser / Playwright tests           |
| `api`        | API-only tests (no browser)          |
| `visual`     | Visual regression tests              |
| `smoke`      | Quick sanity checks (run on every PR)|
| `regression` | Full regression suite                |
| `critical`   | Business-critical paths              |

---

## CI/CD (GitHub Actions)

Add these secrets to your repository (`Settings → Secrets → Actions`):

| Secret          | Value                          |
|-----------------|--------------------------------|
| `BASE_URL`      | `https://your-app.com`         |
| `API_BASE_URL`  | `https://api.your-app.com`     |
| `TEST_USERNAME` | `test@example.com`             |
| `TEST_PASSWORD` | `TestPassword123!`             |

The pipeline runs:
- **Smoke tests** on every pull request
- **API tests** on push to `main` / `develop`
- **UI tests** across Chromium, Firefox, WebKit on push
- **Visual tests** on Chromium; baselines are cached as artifacts
- **Nightly full regression** at 02:00 UTC

HTML reports and screenshots are uploaded as artifacts after each run.

---

## Configuration Reference (`.env`)

| Variable              | Default                          | Description                            |
|-----------------------|----------------------------------|----------------------------------------|
| `BASE_URL`            | `https://your-app.com`           | Frontend base URL                      |
| `API_BASE_URL`        | `https://api.your-app.com`       | API base URL                           |
| `TEST_USERNAME`       | —                                | Login email for test account           |
| `TEST_PASSWORD`       | —                                | Login password                         |
| `BROWSER`             | `chromium`                       | `chromium` / `firefox` / `webkit`      |
| `HEADLESS`            | `true`                           | Run browser headlessly                 |
| `SLOW_MO`             | `0`                              | Delay (ms) between actions             |
| `DEFAULT_TIMEOUT`     | `30000`                          | Element wait timeout (ms)              |
| `NAVIGATION_TIMEOUT`  | `60000`                          | Page load timeout (ms)                 |
| `VISUAL_THRESHOLD`    | `0.2`                            | Max pixel-diff ratio (0–1)             |
| `SCREENSHOT_ON_FAILURE` | `true`                         | Capture screenshot on test failure     |
