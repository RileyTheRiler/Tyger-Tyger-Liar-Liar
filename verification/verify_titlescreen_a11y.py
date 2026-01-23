from playwright.sync_api import sync_playwright, expect

def verify_titlescreen(page):
    page.goto("http://localhost:5173/")

    # Wait for the title screen to load
    # get_by_role("button", name="Start Investigation") verifies that the aria-label is correctly effectively naming the button
    start_btn = page.get_by_role("button", name="Start Investigation")
    exit_btn = page.get_by_role("button", name="Exit System")

    # Assert they exist (verifies aria-label works because get_by_role uses accessible name)
    expect(start_btn).to_be_visible(timeout=10000)
    expect(exit_btn).to_be_visible(timeout=10000)

    print("Buttons found by aria-label!")

    # Focus start button to check focus ring
    start_btn.focus()

    # Take screenshot
    page.screenshot(path="verification/titlescreen_focus.png")
    print("Screenshot taken.")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            verify_titlescreen(page)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()
