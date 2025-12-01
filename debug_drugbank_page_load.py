#!/usr/bin/env python3
"""
Debug script to inspect the DrugBank DDI Checker page and check element visibility
"""
import asyncio
from playwright.async_api import async_playwright


async def debug_drugbank_page():
    """Debug the page loading and element visibility"""
    async with async_playwright() as p:
        # Launch browser (non-headless to see what's happening)
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )

        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )

        page = await context.new_page()

        print("=" * 60)
        print("Navigating to DrugBank DDI Checker page...")
        print("=" * 60)

        # Navigate to the page
        await page.goto("https://dev.drugbank.com/demo/ddi_checker", wait_until='load', timeout=30000)

        # Wait a bit for any dynamic content
        print("Waiting 3 seconds for page to settle...")
        await page.wait_for_timeout(3000)

        # Take screenshot
        await page.screenshot(path='debug_drugbank_page_state.png', full_page=True)
        print("✓ Screenshot saved: debug_drugbank_page_state.png")

        # Save HTML
        html = await page.content()
        with open('debug_drugbank_page_state.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("✓ HTML saved: debug_drugbank_page_state.html")

        print("\n" + "=" * 60)
        print("Checking for key elements...")
        print("=" * 60)

        # Check for input field
        input_selector = "#vs1__combobox > div.vs__selected-options > input"
        input_field = await page.query_selector(input_selector)
        print(f"Input field ({input_selector}): {'✓ FOUND' if input_field else '✗ NOT FOUND'}")

        if not input_field:
            # Try alternative selectors
            print("\n--- Trying alternative input selectors ---")
            alt_input_selectors = [
                "input[type='text']",
                "input[placeholder*='drug']",
                ".vs__selected-options input",
                "#vs1__combobox input",
            ]

            for selector in alt_input_selectors:
                element = await page.query_selector(selector)
                if element:
                    placeholder = await element.get_attribute('placeholder') or ''
                    print(f"  ✓ {selector}: placeholder='{placeholder}'")

        # Check for check interactions button
        button_selector = "body > main > div.panel.plugin-panel > div > div.demo-body > div > div.panel-right.col-right.col-xs-12.col-sm-8 > div > div.row.ddi-controls > center > a.button.dark.check-interactions"
        check_button = await page.query_selector(button_selector)
        print(f"\nCheck button ({button_selector}): {'✓ FOUND' if check_button else '✗ NOT FOUND'}")

        if not check_button:
            # Try alternative selectors
            print("\n--- Trying alternative button selectors ---")
            alt_button_selectors = [
                "a.button.dark.check-interactions",
                "a.check-interactions",
                "a:has-text('Check Interactions')",
                ".ddi-controls a",
            ]

            for selector in alt_button_selectors:
                element = await page.query_selector(selector)
                if element:
                    try:
                        text = await element.inner_text()
                        print(f"  ✓ {selector}: text='{text}'")
                    except:
                        print(f"  ✓ {selector}: (found but couldn't get text)")

        # List all inputs on the page
        print("\n--- All input fields on the page ---")
        inputs = await page.query_selector_all("input")
        for i, inp in enumerate(inputs):
            try:
                inp_id = await inp.get_attribute('id') or '(no id)'
                inp_class = await inp.get_attribute('class') or '(no class)'
                inp_type = await inp.get_attribute('type') or '(no type)'
                inp_placeholder = await inp.get_attribute('placeholder') or '(no placeholder)'
                print(f"  Input {i+1}: id='{inp_id}', type='{inp_type}', placeholder='{inp_placeholder[:50]}'")
            except:
                print(f"  Input {i+1}: (error reading attributes)")

        # List all buttons/links that might be the check button
        print("\n--- All links/buttons with 'check' or 'interaction' ---")
        links = await page.query_selector_all("a, button")
        for i, link in enumerate(links):
            try:
                text = await link.inner_text()
                href = await link.get_attribute('href') or ''
                class_attr = await link.get_attribute('class') or ''

                if text and ('check' in text.lower() or 'interaction' in text.lower()):
                    print(f"  Link {i}: text='{text.strip()}', class='{class_attr}', href='{href[:50]}'")
            except:
                pass

        # Keep browser open for inspection
        print("\n" + "=" * 60)
        print("Browser will stay open for 60 seconds for manual inspection...")
        print("=" * 60)
        await page.wait_for_timeout(60000)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_drugbank_page())
