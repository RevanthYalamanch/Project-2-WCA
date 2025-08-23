import requests
import json

# --- Configuration ---
# This should be the address of your running backend server.
BACKEND_URL = "http://127.0.0.1:8000/analyze"

# --- Test Case Definitions ---
TEST_CASES = [
    # --- Passing Test Cases ---
    {
        "id": "TC-01",
        "description": "Single Valid URL Analysis",
        "url": "https://www.bbc.com/news/science-environment-68090998",
        "expected_status": 200,
        "expected_result": "PASS",
    },
    {
        "id": "TC-02",
        "description": "Batch URL Processing (Simulated - checks another valid URL)",
        "url": "https://www.microsoft.com",
        "expected_status": 200,
        "expected_result": "PASS",
    },
    {
        "id": "TC-03",
        "description": "Graceful 404 Not Found Handling",
        "url": "https://www.google.com/this-page-does-not-exist-12345",
        "expected_status": 400, # The scraper service will raise a ConnectionError
        "expected_result": "PASS",
    },
    {
        "id": "TC-04",
        "description": "Non-HTML Content Type Handling",
        "url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        "expected_status": 400, # The service raises a ValueError for wrong content type
        "expected_result": "PASS",
    },
    # --- Failing Test Cases ---
    {
        "id": "TC-05",
        "description": "Malformed URL Input",
        "url": "this is not a valid url",
        "expected_status": 422, # FastAPI's Unprocessable Entity for Pydantic validation failure
        "expected_result": "FAIL", # The test 'fails' from a user perspective, but the system works correctly
    },
    {
        "id": "TC-06",
        "description": "Server-Side Request Forgery (SSRF) Attempt",
        "url": "http://127.0.0.1",
        "expected_status": 400, # Our security validator should block this
        "expected_result": "FAIL",
    },
    {
        "id": "TC-07",
        "description": "Blacklisted Domain Input",
        "url": "https://www.nasa.gov", # Assumes '.gov' is in the blacklist
        "expected_status": 400, # Our security validator should block this
        "expected_result": "FAIL",
    },
    {
        "id": "TC-08",
        "description": "JavaScript-Reliant Website (with requests-based scraper)",
        "url": "https://react.dev/",
        "expected_status": 500, # The Pydantic model validation for min_length should fail
        "expected_result": "FAIL",
    },
]

def run_tests():
    """
    Executes all defined test cases against the backend API.
    """
    print("--- Starting Web Content Analyzer Test Suite ---")
    passed_count = 0
    failed_count = 0

    for test in TEST_CASES:
        print(f"\n--- Running Test Case: {test['id']} ({test['description']}) ---")
        print(f"URL: {test['url']}")
        
        payload = {"url": test["url"]}
        actual_result = "FAIL"
        
        try:
            response = requests.post(BACKEND_URL, json=payload, timeout=180)
            status_code = response.status_code
            
            print(f"Expected Status: {test['expected_status']}, Got Status: {status_code}")
            
            if status_code == test['expected_status']:
                # For this script, we'll consider the test 'passing' if the system behaves as designed
                # (e.g., correctly rejecting a bad URL).
                print(f"Result: System behaved as expected. Test PASSED.")
                passed_count += 1
            else:
                print(f"Result: System did NOT behave as expected. Test FAILED.")
                print(f"Response Body: {response.text}")
                failed_count += 1

        except requests.exceptions.RequestException as e:
            print(f"An error occurred during the request: {e}")
            print(f"Result: Test FAILED due to exception.")
            failed_count += 1
            
    print("\n--- Test Suite Summary ---")
    print(f"Total Tests: {len(TEST_CASES)}")
    print(f"✅ Passed: {passed_count}")
    print(f"❌ Failed: {failed_count}")
    print("--------------------------")


if __name__ == "__main__":
    run_tests()