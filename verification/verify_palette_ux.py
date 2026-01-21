import os
from playwright.sync_api import sync_playwright, expect

def verify_title_screen_a11y(page):
    print("Navigating to Title Screen...")
    page.goto("http://localhost:5173/")

    # Wait for the main title to appear (it has an animation)
    page.wait_for_selector(".title-main", state="visible")

    # Verify semantic structure
    print("Verifying semantic headings...")
    # Check if title-main is an h1
    title_main = page.locator(".title-main")
    # In the updated code, GlitchText should render as h1
    # Note: GlitchText uses the `as` prop which sets the tag.
    # We need to verify if the rendered element is indeed an h1.

    # Wait for the element to be attached
    title_main.wait_for(state="attached")

    # Get the tag name. GlitchText renders <Tag class="glitch-wrapper ...">
    # So we check if there is an h1 with class title-main
    expect(page.locator("h1.title-main")).to_be_visible()
    print("✅ h1.title-main found")

    expect(page.locator("h2.title-sub")).to_be_visible()
    print("✅ h2.title-sub found")

    # Verify ARIA labels on buttons
    print("Verifying button ARIA labels...")
    start_btn = page.get_by_label("Start Investigation")
    expect(start_btn).to_be_visible()
    print("✅ Start button with aria-label found")

    exit_btn = page.get_by_label("Exit System")
    expect(exit_btn).to_be_visible()
    print("✅ Exit button with aria-label found")

    # Verify focus states
    print("Verifying focus states...")
    start_btn.focus()
    page.wait_for_timeout(500) # Wait for transition
    page.screenshot(path="verification/focus_start.png")
    print("📸 Screenshot of focused start button saved to verification/focus_start.png")

    exit_btn.focus()
    page.wait_for_timeout(500)
    page.screenshot(path="verification/focus_exit.png")
    print("📸 Screenshot of focused exit button saved to verification/focus_exit.png")

    # General screenshot
    page.screenshot(path="verification/title_screen.png")
    print("📸 General screenshot saved to verification/title_screen.png")

if __name__ == "__main__":
    os.makedirs("verification", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_title_screen_a11y(page)
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            page.screenshot(path="verification/error.png")
        finally:
            browser.close()
