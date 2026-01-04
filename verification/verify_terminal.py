from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Navigate to the frontend dev server (assuming it will be running)
        page.goto("http://localhost:5173")

        # Wait for the Title Screen "Start Investigation" button or any indicator
        try:
            # Wait for title screen content
            page.wait_for_selector(".title-screen", timeout=10000)

            # Click start to go to the main terminal view
            page.click("button:has-text(\"[START_INVESTIGATION]\")")

            # Since the API is not running, we might see an error screen or "NO SIGNAL" or just stuck loading.
            # But the terminal renders the initial history if startGame fails (caught in catch block).
            # "ERROR: CONNECTION_LOST_TO_MAINFRAME"

            # Wait for terminal input to appear (or the error message in terminal)
            page.wait_for_selector(".terminal-window", timeout=10000)

            # Take screenshot of Terminal
            page.screenshot(path="verification/terminal_optimization.png")
            print("Screenshot captured.")
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification/error.png")

        browser.close()

if __name__ == "__main__":
    run()
