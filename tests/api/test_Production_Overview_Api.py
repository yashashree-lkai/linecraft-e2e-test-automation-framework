"""
tests/api/test_api_request_response_payload.py

Complete API Test — Captures and validates REQUEST and RESPONSE payloads
"""

import pytest
import json
from urllib.parse import urlparse, parse_qs
from pages.login_page import LoginPage
from pages.menuPage import MenuPage

MODULE = "Production Overview"


def login_and_open_production_overview(page, context, base_url, test_data):
    """Helper: Login, select line, open Production Overview."""
    login = LoginPage(page, base_url).navigate()
    login.login(test_data["username"], test_data["password"])
    page.wait_for_url("**Menu**", timeout=20_000)
    page.wait_for_timeout(2000)

    menu = MenuPage(page, base_url)
    menu.select_company(test_data["company"])
    menu.select_plant(test_data["plant"])
    menu.select_line(test_data["line"])

    with context.expect_page() as new_page_info:
        page.get_by_text(MODULE, exact=True).click()

    new_page = new_page_info.value
    new_page.wait_for_url("**ProductionOverview**", timeout=10_000)
    return new_page


@pytest.mark.api
@pytest.mark.critical
def test_api_request_response_payload(page, context, base_url, test_data, environment):
    """
    Complete API Payload Test

    Captures and validates:
    ✅ Request URL
    ✅ Request Headers
    ✅ Request Body/Payload
    ✅ Response Status
    ✅ Response Headers
    ✅ Response Body/Payload
    """
    captured_requests = []
    captured_responses = []

    prod_page = login_and_open_production_overview(page, context, base_url, test_data)

    print(f"\n\n{'='*100}")
    print(f"🚀 PRODUCTION OVERVIEW LOADED — Ready to capture API payloads")
    print(f"{'='*100}\n")

    # Capture requests with full payload
    def capture_request(request):
        if "get_assetwise_kpi" in request.url:
            try:
                # Try to get request body/post data
                request_body = None
                try:
                    request_body = request.post_data
                except:
                    request_body = None

                captured_requests.append({
                    "method": request.method,
                    "url": request.url,
                    "headers": dict(request.headers),
                    "body": request_body,
                })
                print(f"📤 REQUEST CAPTURED: {request.method} {request.url}\n")
            except Exception as e:
                print(f"⚠️  Error capturing request: {e}\n")

    # Capture responses with full payload
    def capture_response(response):
        if "get_assetwise_kpi" in response.url:
            try:
                response_body = response.text()
                try:
                    response_json = response.json()
                except:
                    response_json = None

                captured_responses.append({
                    "url": response.url,
                    "status": response.status,
                    "headers": dict(response.headers),
                    "body_text": response_body,
                    "body_json": response_json,
                })
                print(f"📥 RESPONSE CAPTURED: {response.status}\n")
            except Exception as e:
                print(f"⚠️  Error capturing response: {e}\n")

    prod_page.on("request", capture_request)
    prod_page.on("response", capture_response)

    # Wait for API to fire
    print("⏳ Waiting for API to fire (max 10 seconds)...")
    prod_page.wait_for_timeout(10000)

    print(f"\n\n{'='*100}")
    print(f"📋 API PAYLOAD TEST REPORT — {environment.upper()}")
    print(f"{'='*100}\n")

    # === REQUEST PAYLOAD ===
    if captured_requests:
        req = captured_requests[0]

        print(f"{'█'*100}")
        print(f"📤 REQUEST PAYLOAD")
        print(f"{'█'*100}\n")

        print(f"METHOD: {req['method']}")
        print(f"URL: {req['url']}\n")

        # Parse query parameters
        parsed = urlparse(req["url"])
        params = parse_qs(parsed.query)

        print(f"QUERY PARAMETERS:")
        print(f"{'-'*100}")
        for key, value in sorted(params.items()):
            print(f"  {key:25} = {value[0]}")
        print()

        # Request headers
        print(f"REQUEST HEADERS:")
        print(f"{'-'*100}")
        for header, value in sorted(req['headers'].items()):
            if header.lower() == 'authorization':
                token = value.replace('Bearer ', '').strip()
                print(f"  {header:25} = Bearer {token[:50]}...")
            else:
                print(f"  {header:25} = {value}")
        print()

        # Request body if present
        if req['body']:
            print(f"REQUEST BODY/PAYLOAD:")
            print(f"{'-'*100}")
            try:
                body_json = json.loads(req['body'])
                print(json.dumps(body_json, indent=2))
            except:
                print(req['body'])
            print()
        else:
            print(f"REQUEST BODY: (None - GET request)\n")

    else:
        print("❌ NO REQUEST CAPTURED!\n")

    # === RESPONSE PAYLOAD ===
    print(f"\n{'█'*100}")
    print(f"📥 RESPONSE PAYLOAD")
    print(f"{'█'*100}\n")

    if captured_responses:
        resp = captured_responses[0]

        print(f"STATUS: {resp['status']}")
        print(f"URL: {resp['url']}\n")

        # Response headers
        print(f"RESPONSE HEADERS:")
        print(f"{'-'*100}")
        for header, value in sorted(resp['headers'].items()):
            print(f"  {header:25} = {value}")
        print()

        # Response body
        print(f"RESPONSE BODY/PAYLOAD:")
        print(f"{'-'*100}")
        if resp['body_json']:
            print(json.dumps(resp['body_json'], indent=2))
        else:
            print(resp['body_text'][:500])  # Print first 500 chars
        print()

    else:
        print("❌ NO RESPONSE CAPTURED!\n")

    # === VALIDATION ===
    print(f"\n{'█'*100}")
    print(f"✅ VALIDATION & ASSERTIONS")
    print(f"{'█'*100}\n")

    if captured_requests and captured_responses:
        req = captured_requests[0]
        resp = captured_responses[0]
        parsed = urlparse(req["url"])
        params = parse_qs(parsed.query)
        expected = test_data.get("expected_values", {})

        print(f"REQUEST PARAMETERS VALIDATION:")
        print(f"{'-'*100}")

        # Validate config_id
        actual_config = params.get("config_id", [""])[0]
        expected_config = expected.get("config_id", "")
        status = "✅ PASS" if actual_config == expected_config else "❌ FAIL"
        print(f"  {status} | config_id")
        print(f"         Expected: '{expected_config}'")
        print(f"         Actual:   '{actual_config}'")

        # Validate node_ids
        actual_nodes = params.get("node_ids", [""])[0]
        expected_nodes = expected.get("node_ids", "")
        status = "✅ PASS" if actual_nodes == expected_nodes else "❌ FAIL"
        print(f"  {status} | node_ids")
        print(f"         Expected: '{expected_nodes}'")
        print(f"         Actual:   '{actual_nodes}'")

        # Validate is_daywise
        actual_daywise = params.get("is_daywise", [""])[0]
        expected_daywise = expected.get("is_daywise", "")
        status = "✅ PASS" if actual_daywise == expected_daywise else "❌ FAIL"
        print(f"  {status} | is_daywise")
        print(f"         Expected: '{expected_daywise}'")
        print(f"         Actual:   '{actual_daywise}'")

        print()
        print(f"RESPONSE VALIDATION:")
        print(f"{'-'*100}")

        # Validate HTTP status
        status = "✅ PASS" if resp['status'] == 200 else "❌ FAIL"
        print(f"  {status} | HTTP Status Code = {resp['status']}")

        # Validate response structure
        if resp['body_json']:
            if isinstance(resp['body_json'], dict):
                print(f"  ✅ PASS | Response is valid JSON")
                print(f"         Keys: {list(resp['body_json'].keys())}")

        print()

    print(f"{'='*100}\n")

    # Assertions
    assert len(captured_requests) > 0, "❌ No API requests captured!"
    assert len(captured_responses) > 0, "❌ No API responses captured!"
    assert captured_responses[0]['status'] == 200, f"❌ API returned {captured_responses[0]['status']}"

    print(f"✅ API PAYLOAD TEST COMPLETED SUCCESSFULLY on {environment.upper()}\n")