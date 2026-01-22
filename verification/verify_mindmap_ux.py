from playwright.sync_api import sync_playwright, expect
import time

def test_mindmap_ux(page):
    page.on("console", lambda msg: print(f"PAGE LOG: {msg.text}"))
    # Mock API responses
    page.route("**/api/start", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='''{
            "output": "SYSTEM ONLINE",
            "state": {
                "sanity": 80,
                "reality": 90,
                "location": "TEST LAB",
                "time": "12:00",
                "day": "1",
                "board_data": {
                    "nodes": [
                        {"id": "t1", "type": "theory", "label": "THEORY 1", "health": 80, "status": "active", "is_strained": false, "is_glitched": false},
                        {"id": "e1", "type": "evidence", "label": "EVIDENCE A", "x": 0, "y": 0}
                    ],
                    "links": [
                        {"source": "t1", "target": "e1", "has_friction": false}
                    ]
                }
            }
        }'''
    ))

    # Go to app
    print("Navigating to app...")
    page.goto("http://localhost:5174/")

    # Click Start button on Title Screen
    print("Clicking Start...")
    page.locator(".start-btn").click()

    # Wait for the [VIEW_MINDMAP] button to be visible (after boot sequence)
    print("Waiting for boot sequence...")
    # Increase timeout to 15s to be safe
    page.get_by_text("[VIEW_MINDMAP]").wait_for(timeout=15000)

    # 1. Open MindMap
    print("Opening MindMap...")
    page.get_by_text("[VIEW_MINDMAP]").click()

    # Check if MindMap is visible
    mindmap = page.get_by_role("dialog", name="Case Logic Graph")
    expect(mindmap).to_be_visible()

    # Take screenshot of open state
    page.screenshot(path="verification/mindmap_open.png")
    print("MindMap Opened. Screenshot saved.")

    # 2. Test Escape Key
    print("Testing Escape Key...")
    page.keyboard.press("Escape")

    # Check if MindMap is closed
    expect(mindmap).not_to_be_visible()
    print("MindMap Closed via Escape.")

    # 3. Test Backdrop Click
    print("Testing Backdrop Click...")
    page.get_by_text("[VIEW_MINDMAP]").click()
    expect(mindmap).to_be_visible()

    # Click the backdrop (top left corner 10,10)
    # The overlay covers the whole screen
    # page.mouse.click(10, 10)
    # Use element handle to click specifically on the overlay, at the edge
    # mindmap.click(position={"x": 5, "y": 5}, force=True)

    # Try forcing a click event via JS
    mindmap.evaluate("el => el.click()")

    expect(mindmap).not_to_be_visible()
    print("MindMap Closed via Backdrop Click.")

    # Take final screenshot
    page.screenshot(path="verification/mindmap_closed.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            test_mindmap_ux(page)
        except Exception as e:
            print(f"Test failed: {e}")
            page.screenshot(path="verification/failure.png")
            raise
        finally:
            browser.close()
