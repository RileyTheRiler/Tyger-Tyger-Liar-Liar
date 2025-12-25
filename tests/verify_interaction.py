import os
import sys
from playwright.sync_api import sync_playwright

def verify_interaction():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        cwd = os.getcwd()
        file_path = os.path.join(cwd, "title_screen", "index.html")
        url = f"file://{file_path}"

        print(f"Loading: {url}")
        page.goto(url)
        page.wait_for_timeout(1000)

        # Check initial state (first item active)
        first_item = page.locator(".main-menu li").first
        first_crt = page.locator(".crt-menu li").first

        # get_attribute("class") might return None or "some-class active"
        cls = first_item.get_attribute("class") or ""
        if "active" not in cls:
            print(f"FAILURE: First item not active initially. Class: '{cls}'")
            sys.exit(1)

        cls_crt = first_crt.get_attribute("class") or ""
        if "active" not in cls_crt:
            print(f"FAILURE: First CRT item not active initially. Class: '{cls_crt}'")
            sys.exit(1)

        print("Initial state correct.")

        # Press Down Arrow
        page.keyboard.press("ArrowDown")
        page.wait_for_timeout(200)

        # Check second item active
        items = page.locator(".main-menu li")

        cls_1 = items.nth(1).get_attribute("class") or ""
        if "active" not in cls_1:
            print(f"FAILURE: Second item not active after ArrowDown. Class: '{cls_1}'")
            sys.exit(1)

        cls_0 = items.first.get_attribute("class") or ""
        if "active" in cls_0:
            print(f"FAILURE: First item still active after ArrowDown. Class: '{cls_0}'")
            sys.exit(1)

        print("Keyboard navigation correct.")

        # Check Mouse Hover
        # Hover over 3rd item
        items.nth(2).hover()
        page.wait_for_timeout(200)

        cls_2 = items.nth(2).get_attribute("class") or ""
        if "active" not in cls_2:
            print(f"FAILURE: Third item not active after hover. Class: '{cls_2}'")
            sys.exit(1)

        cls_1 = items.nth(1).get_attribute("class") or ""
        if "active" in cls_1:
            print(f"FAILURE: Second item still active after hover. Class: '{cls_1}'")
            sys.exit(1)

        print("Mouse hover correct.")

        browser.close()

if __name__ == "__main__":
    verify_interaction()
