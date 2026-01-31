
from playwright.sync_api import sync_playwright, expect

def verify_a11y(page):
    print("Navigating to app...")
    page.goto("http://localhost:5173")

    print("Checking Title Screen...")
    # Wait for the title screen to load
    page.wait_for_selector(".title-screen")

    # Check Start Button
    start_btn = page.locator(".start-btn")
    expect(start_btn).to_be_visible()

    # Check aria-label
    aria_label = start_btn.get_attribute("aria-label")
    print(f"Start Button aria-label: {aria_label}")
    assert aria_label == "Start Investigation", f"Expected 'Start Investigation', got '{aria_label}'"

    # Check inner span aria-hidden
    hidden_span = start_btn.locator("span[aria-hidden='true']")
    expect(hidden_span).to_be_visible()
    print("Start Button has aria-hidden span.")

    # Check Exit Button
    exit_btn = page.locator(".exit-btn")
    expect(exit_btn).to_be_visible()
    aria_label_exit = exit_btn.get_attribute("aria-label")
    print(f"Exit Button aria-label: {aria_label_exit}")
    assert aria_label_exit == "Exit System", f"Expected 'Exit System', got '{aria_label_exit}'"

    # Screenshot
    page.screenshot(path="verification/a11y_verification.png")
    print("Screenshot saved to verification/a11y_verification.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_a11y(page)
        except Exception as e:
            print(f"Verification failed: {e}")
            # Take screenshot on failure
            page.screenshot(path="verification/failure.png")
        finally:
            browser.close()
