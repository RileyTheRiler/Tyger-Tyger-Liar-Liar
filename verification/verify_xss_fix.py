from playwright.sync_api import sync_playwright, expect
import time
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        # Mock api/start to return a malicious payload that should be escaped
        # and a formatted payload that should be rendered HTML
        malicious_input = "<img src=x onerror=alert('XSS')>"
        formatted_input = "**BOLD**"

        # We combine them into the output
        mock_output = f"SAFE: {malicious_input} FORMATTED: {formatted_input}"

        page.route("**/api/start", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=f'{{"output": "{mock_output}", "state": {{"sanity": 100, "reality": 100, "location": "HQ", "time": "08:00", "day": "14"}}}}'
        ))

        try:
            print("Navigating to http://localhost:5173")
            page.goto("http://localhost:5173", timeout=60000)
        except Exception as e:
            print(f"Navigation failed: {e}")
            return

        print("Page loaded")

        # Start game
        start_btn = page.get_by_role("button", name="[START_INVESTIGATION]")
        start_btn.wait_for(timeout=10000)
        start_btn.click()

        # Wait for Terminal
        terminal = page.locator(".terminal-window")
        terminal.wait_for(timeout=10000)

        # Check that the text is visible
        # expect(page.get_by_text(mock_output)).to_be_visible() # This might fail if it renders as HTML

        # We need to inspect the innerHTML of the span that contains this text
        # The structure is .term-line > span > (dangerous HTML)

        # Let's find the term-line that contains our text
        # Since it's the start message, it should be the first term-output
        term_line = page.locator(".term-output .term-line").first
        span = term_line.locator("span").nth(1) # nth(0) is prompt if input, but this is output. Wait, output doesn't have prompt.

        # Actually TerminalEntry renders:
        # {isInput && ...} <span dangerouslySetInnerHTML ... />
        # So for output, it's the first child or so.

        # Let's just get the innerHTML of the span
        # We expect the innerHTML to contain encoded entities for the image tag
        # And actual <strong> tags for the bold part.

        # For output, there is only one span (the content).
        # We need to make sure we are targeting the right span.
        # .term-line has a Motion.div wrapper.

        span = term_line.locator("span").first

        # Using evaluate to get innerHTML
        inner_html = span.evaluate("el => el.innerHTML")
        print(f"Rendered HTML: {inner_html}")

        # Verification Logic
        if "&lt;img" in inner_html and "onerror" in inner_html:
            print("PASS: <img tag was escaped.")
        else:
            print("FAIL: <img tag was NOT properly escaped or found.")

        if "<strong>BOLD</strong>" in inner_html:
            print("PASS: **BOLD** was correctly formatted to <strong>.")
        else:
            print("FAIL: **BOLD** was not formatted correctly.")

        # Take screenshot for manual inspection
        os.makedirs("verification", exist_ok=True)
        page.screenshot(path="verification/xss_verification.png")

        browser.close()

if __name__ == "__main__":
    run()
