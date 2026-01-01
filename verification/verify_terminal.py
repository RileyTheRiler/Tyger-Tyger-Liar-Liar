from playwright.sync_api import sync_playwright, expect
import time

def verify_terminal(page):
    # Capture console logs
    page.on("console", lambda msg: print(f"Browser Console: {msg.text}"))
    page.on("pageerror", lambda err: print(f"Browser Error: {err}"))

    print("Navigating to app...")
    page.goto("http://localhost:5173")

    print("Waiting for body...")
    page.wait_for_selector("body")

    # Wait for title screen to animate in
    time.sleep(2)

    print("Attempting to start game...")
    # Click the start button based on text seen in screenshot
    try:
        # Try finding the button by text
        start_btn = page.get_by_text("[START_INVESTIGATION]")
        if start_btn.is_visible():
            start_btn.click()
        else:
            # Fallback to generic click if text is split or animated weirdly
            print("Button not found by text, clicking center...")
            page.mouse.click(500, 500)
    except Exception as e:
        print(f"Click failed: {e}")
        page.mouse.click(500, 500)

    # Wait for boot sequence (it says "Waiting for boot sequence..." in logs, implies delay)
    print("Waiting for boot sequence...")
    # App.jsx has BootSequence component. It might take some time.
    # We can wait for .terminal-window to appear.

    print("Checking for terminal window...")
    terminal = page.locator(".terminal-window")

    try:
        terminal.wait_for(state="visible", timeout=15000)
        print("Terminal is visible!")

        # Verify content inside
        # Check if there is at least one terminal entry
        entry = page.locator(".term-entry").first
        expect(entry).to_be_visible()

        page.screenshot(path="verification/terminal_verification.png")
    except Exception as e:
        print(f"Terminal check failed: {e}")
        print("Taking failure screenshot...")
        page.screenshot(path="verification/failure.png")
        raise e

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_terminal(page)
        except Exception as e:
            print(f"Verification failed: {e}")
        finally:
            browser.close()
