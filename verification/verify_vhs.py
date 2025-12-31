from playwright.sync_api import sync_playwright

def verify_vhs_effect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Create context with reduced motion to ensure consistent rendering for snapshots if possible,
        # though our effect is specifically about motion.
        context = browser.new_context()
        page = context.new_page()

        # Navigate to the frontend dev server
        try:
            page.goto("http://localhost:5173", timeout=30000)

            # Wait for the VHS effect container to be present in the DOM
            # The component has class 'vhs-container'
            page.wait_for_selector(".vhs-container", timeout=10000)

            # Wait a moment for the effect to initialize and run a few frames
            page.wait_for_timeout(2000)

            # Take a screenshot
            screenshot_path = "verification/vhs_effect.png"
            page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")

            # Basic validation that elements exist
            noise = page.locator(".static-noise")
            tracking = page.locator(".tracking-bar")
            glitch = page.locator(".glitch-overlay")

            if noise.count() > 0 and tracking.count() > 0 and glitch.count() > 0:
                print("All VHS effect elements found.")
            else:
                print("Error: specific VHS elements not found.")

        except Exception as e:
            print(f"Error during verification: {e}")
            page.screenshot(path="verification/error_state.png")

        finally:
            browser.close()

if __name__ == "__main__":
    verify_vhs_effect()
