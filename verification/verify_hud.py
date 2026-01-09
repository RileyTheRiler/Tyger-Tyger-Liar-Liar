import time
from playwright.sync_api import sync_playwright, expect

def verify_hud():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # We need to grant permissions if audio is involved or just load the page
        context = browser.new_context()
        page = context.new_page()

        # Intercept the API call to start_game so we can inject a mock state
        # The frontend calls /api/start
        def handle_start(route):
            print("Intercepted /api/start")
            route.fulfill(
                status=200,
                content_type="application/json",
                body='{"output": "Welcome Agent.", "state": {"sanity": 75, "reality": 20, "location": "Kaltvik", "time": "08:00", "day": "14", "choices": [], "board_data": {}, "music": null}}'
            )

        page.route("**/api/start", handle_start)

        print("Navigating to app...")
        page.goto("http://localhost:5173")

        # Wait for Title Screen and click Start
        # The button text is "[START_INVESTIGATION]"
        print("Waiting for Title Screen...")
        page.get_by_role("button", name="[START_INVESTIGATION]").click()

        # Wait for Boot Sequence (it takes some time)
        print("Waiting for Boot Sequence...")

        # The HUD container is rendered when !booting.
        # We can wait for the text "BIO_MONITOR_v9" which is in the HUD.
        # Increasing timeout to be safe.
        page.wait_for_selector("text=BIO_MONITOR_v9", timeout=15000)
        print("HUD detected.")

        # Now we verify our changes
        # 1. Check AnalogGauge for Sanity (Value 75)
        sanity_gauge = page.locator("[role='progressbar']").filter(has_text="SANITY")
        expect(sanity_gauge).to_be_visible()
        expect(sanity_gauge).to_have_attribute("aria-valuenow", "75")
        expect(sanity_gauge).to_have_attribute("aria-valuemin", "0")
        expect(sanity_gauge).to_have_attribute("aria-valuemax", "100")
        print("Sanity Gauge verified.")

        # 2. Check AnalogGauge for Reality (Value 20)
        reality_gauge = page.locator("[role='progressbar']").filter(has_text="REALITY")
        expect(reality_gauge).to_be_visible()
        expect(reality_gauge).to_have_attribute("aria-valuenow", "20")
        print("Reality Gauge verified.")

        # 3. Check Warning Box
        # Since Reality is 20 (< 30), the warning box should be visible.
        # It should have role="alert"
        warning_box = page.locator("[role='alert']")
        expect(warning_box).to_be_visible()
        expect(warning_box).to_contain_text("REALITY FRACTURE")
        print("Warning Box verified.")

        # Take a screenshot
        page.screenshot(path="verification/hud_accessible.png")
        print("Screenshot taken.")

        browser.close()

if __name__ == "__main__":
    verify_hud()
