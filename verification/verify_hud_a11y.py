from playwright.sync_api import sync_playwright, expect

def verify_hud_a11y():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Mocking the /api/start endpoint is required according to memory
        # "Frontend verification of StatusHUD requires mocking the /api/start response... otherwise App.jsx fails to initialize"

        context = browser.new_context()
        page = context.new_page()

        # Route the /api/start to return a valid initial state
        def handle_start(route):
            route.fulfill(json={
                "output": "SYSTEM ONLINE",
                "state": {
                    "sanity": 75,
                    "reality": 80,
                    "location": "TEST LAB",
                    "time": "12:00",
                    "day": 1
                }
            })

        page.route("**/api/start", handle_start)

        try:
            print("Navigating to app...")
            page.goto("http://localhost:5173")

            # Wait for the boot sequence (approx 4.4s) and click start
            print("Waiting for start button...")
            # Using a broad selector or waiting for text as the start button might be an overlay
            start_button = page.get_by_text("[START_INVESTIGATION]")
            start_button.wait_for(timeout=10000)
            start_button.click()

            print("Waiting for StatusHUD...")
            # Wait for StatusHUD to appear
            page.get_by_text("BIO_MONITOR_v9").wait_for()

            # Verify ARIA attributes on AnalogGauge (SANITY)
            sanity_gauge = page.locator("div[role='progressbar'][aria-label='SANITY']")
            expect(sanity_gauge).to_be_visible()
            expect(sanity_gauge).to_have_attribute("aria-valuenow", "75")
            print("Verified SANITY gauge attributes.")

            # Verify ARIA attributes on AnalogGauge (REALITY)
            reality_gauge = page.locator("div[role='progressbar'][aria-label='REALITY']")
            expect(reality_gauge).to_be_visible()
            expect(reality_gauge).to_have_attribute("aria-valuenow", "80")
            print("Verified REALITY gauge attributes.")

            # Verify Input Console ARIA label
            input_field = page.get_by_label("Command input")
            expect(input_field).to_be_visible()
            print("Verified Input Console label.")

            # Take screenshot
            page.screenshot(path="verification/hud_a11y.png")
            print("Screenshot saved to verification/hud_a11y.png")

        except Exception as e:
            print(f"Verification failed: {e}")
            page.screenshot(path="verification/error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_hud_a11y()
