"""
conftest.py — Auto-detects environment and loads flexible test data.
Works with config/environments.json for multi-environment testing.
"""

import json
import pytest
from dotenv import load_dotenv

# Load base .env (non-sensitive settings only)
load_dotenv(".env")


def pytest_addoption(parser):
    """Add custom command-line options."""
    parser.addoption(
        "--env",
        action="store",
        default="auto",
        help="Environment: internal, production, staging, or auto (detect from base_url)",
    )


@pytest.fixture(scope="session")
def config_data():
    """Load environments.json with test data for each environment."""
    with open("config/environments.json") as f:
        return json.load(f)


def detect_environment(base_url, config_data):
    """Auto-detect environment from base_url."""
    for env_name, env_config in config_data.items():
        if env_config["base_url"] in base_url:
            return env_name
    return "internal"  # Default fallback


@pytest.fixture(scope="session")
def environment(request, config_data):
    """Determine which environment we're testing."""
    env = request.config.getoption("--env")
    base_url = request.config.getoption("--base-url")

    if env == "auto":
        env = detect_environment(base_url, config_data)

    print(f"\n{'='*70}")
    print(f"🌍 ENVIRONMENT: {env.upper()}")
    print(f"🔗 URL: {base_url}")
    print(f"{'='*70}\n")

    return env


@pytest.fixture(scope="session")
def test_data(request, config_data, environment):
    """Get test data (credentials, company, plant, line, APIs) for current environment."""
    return config_data[environment]


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Set browser context arguments."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
    }


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "ui: UI / browser tests")
    config.addinivalue_line("markers", "api: API tests")
    config.addinivalue_line("markers", "visual: Visual regression tests")
    config.addinivalue_line("markers", "smoke: Smoke tests (quick)")
    config.addinivalue_line("markers", "regression: Full regression suite")
    config.addinivalue_line("markers", "critical: Business-critical tests")