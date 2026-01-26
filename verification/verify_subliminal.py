from playwright.sync_api import sync_playwright, expect
import time

def run(page):
    print("Navigating to app...")
    # Mock /api/start
    page.route("**/api/start", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"output": "Welcome agent.", "state": {"sanity": 80, "reality": 90, "location": "OFFICE", "time": "09:00", "day": 14, "archetype": "neutral"}}'
    ))

    # Mock /api/health if needed
    page.route("**/api/health", lambda route: route.fulfill(status=200, body='{"status": "ok"}'))

    page.goto("http://localhost:5173")

    print("Clicking Start...")
    # Click start button on title screen
    page.get_by_role("button", name="[START_INVESTIGATION]").click()

    print("Waiting for boot sequence...")
    # Wait for StatusHUD to appear. The boot sequence takes some time.
    # The .hud-title contains the SubliminalText
    page.wait_for_selector(".hud-title", timeout=15000)

    print("Verifying SubliminalText structure...")

    # Locate the container
    hud_title = page.locator(".hud-title")

    # Verify sr-only span exists
    sr_only = hud_title.locator(".sr-only")
    expect(sr_only).to_have_text("BIO_MONITOR_v9")

    # Verify it has the correct styles (roughly) to be hidden
    # We can check the class attribute
    expect(sr_only).to_have_class("sr-only")

    # Verify visible part exists and is aria-hidden
    visible_part = hud_title.locator("span[aria-hidden='true']")
    expect(visible_part).to_be_visible()
    expect(visible_part).to_have_text("BIO_MONITOR_v9")

    # Take screenshot
    page.screenshot(path="/home/jules/verification/subliminal_verification.png")
    print("Verification successful!")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            run(page)
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="/home/jules/verification/error.png")
            raise
        finally:
            browser.close()
