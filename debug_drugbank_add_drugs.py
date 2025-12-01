#!/usr/bin/env python3
"""
Debug script to add drugs to DrugBank and inspect the interaction results structure
"""
import asyncio
from playwright.async_api import async_playwright


async def debug_drugbank_add_drugs():
    """Add two drugs and inspect the resulting page structure"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )

        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )

        page = await context.new_page()

        print("Navigating to DrugBank DDI Checker page...")
        await page.goto("https://dev.drugbank.com/demo/ddi_checker", wait_until='load')
        await page.wait_for_timeout(2000)

        # Take screenshot of initial state
        await page.screenshot(path='debug_drugbank_1_initial.png')
        print("✓ Initial state screenshot saved")

        # Input selector
        input_selector = "#vs1__combobox > div.vs__selected-options > input"

        # Add first drug
        print("\n--- Adding first drug: Lisinopril ---")
        await page.fill(input_selector, "")
        await page.wait_for_timeout(500)
        await page.type(input_selector, "Lisinopril", delay=100)
        print("✓ Typed 'Lisinopril'")

        await page.wait_for_timeout(1000)
        print("Waiting for dropdown...")

        await page.keyboard.press('Enter')
        print("✓ Pressed Enter")
        await page.wait_for_timeout(2000)

        # Take screenshot after adding first drug
        await page.screenshot(path='debug_drugbank_2_after_first_drug.png')
        print("✓ Screenshot after first drug saved")

        # Save HTML
        html = await page.content()
        with open('debug_drugbank_after_first_drug.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("✓ HTML saved: debug_drugbank_after_first_drug.html")

        # Add second drug
        print("\n--- Adding second drug: Amlodipine ---")
        await page.fill(input_selector, "")
        await page.wait_for_timeout(500)
        await page.type(input_selector, "Amlodipine", delay=100)
        print("✓ Typed 'Amlodipine'")

        await page.wait_for_timeout(1000)
        print("Waiting for dropdown...")

        await page.keyboard.press('Enter')
        print("✓ Pressed Enter")
        await page.wait_for_timeout(2000)

        # Take screenshot after adding second drug
        await page.screenshot(path='debug_drugbank_3_after_second_drug.png')
        print("✓ Screenshot after second drug saved")

        # Save HTML after second drug
        html = await page.content()
        with open('debug_drugbank_after_second_drug.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("✓ HTML saved: debug_drugbank_after_second_drug.html")

        # Now check for the "Check Interactions" button
        print("\n--- Looking for 'Check Interactions' button ---")
        check_selectors = [
            "body > main > div.panel.plugin-panel > div > div.demo-body > div > div.panel-right.col-right.col-xs-12.col-sm-8 > div > div.row.ddi-controls > center > a.button.dark.check-interactions",
            "a.button.dark.check-interactions",
            "a.check-interactions",
            "a:has-text('Check Interactions')",
            ".ddi-controls a",
        ]

        for selector in check_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.inner_text()
                    href = await element.get_attribute('href') or ''
                    class_attr = await element.get_attribute('class') or ''
                    print(f"  ✓ {selector}: text='{text}', class='{class_attr}', href='{href}'")
            except Exception as e:
                print(f"  ✗ {selector}: {str(e)}")

        # Click the button if found
        print("\n--- Attempting to click 'Check Interactions' button ---")
        try:
            button_selector = "a.button.dark.check-interactions"
            await page.click(button_selector)
            print(f"✓ Clicked button with selector: {button_selector}")
            await page.wait_for_timeout(3000)
            print("Waited 3 seconds for results to load")

            # Take screenshot after clicking
            await page.screenshot(path='debug_drugbank_4_after_check.png', full_page=True)
            print("✓ Screenshot after check saved")

            # Save HTML after clicking
            html = await page.content()
            with open('debug_drugbank_after_check.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("✓ HTML saved: debug_drugbank_after_check.html")

            # Check for results
            print("\n--- Looking for interaction results ---")

            # Check for result container
            result_container_selector = "div > div > div.ddi-widget-body > div > div.form-row.mb-3"
            result_containers = await page.query_selector_all(result_container_selector)
            print(f"Result containers found: {len(result_containers)}")

            # Check for severity
            severity_selector = "div > div > div.ddi-widget-body > div > div.form-row.mb-3 > div > div > div.card-row.header-row > div.intx-item.interaction-severity"
            severity_elements = await page.query_selector_all(severity_selector)
            print(f"Severity elements found: {len(severity_elements)}")

            for i, elem in enumerate(severity_elements):
                text = await elem.inner_text()
                print(f"  Severity {i+1}: '{text}'")

            # Check for description
            description_selector = "div > div > div.ddi-widget-body > div > div.form-row.mb-3 > div > div > div:nth-child(2)"
            description_elements = await page.query_selector_all(description_selector)
            print(f"Description elements found: {len(description_elements)}")

            for i, elem in enumerate(description_elements):
                text = await elem.inner_text()
                print(f"  Description {i+1} preview: '{text[:100]}...'")

            # Try alternative selectors
            print("\n--- Trying alternative result selectors ---")
            alt_selectors = [
                ".ddi-widget-body",
                ".form-row.mb-3",
                ".intx-item.interaction-severity",
                "[class*='severity']",
                "[class*='interaction']",
            ]

            for selector in alt_selectors:
                elements = await page.query_selector_all(selector)
                print(f"  {selector}: {len(elements)} found")

        except Exception as e:
            print(f"Error clicking button or checking results: {str(e)}")

        # Keep browser open
        print("\n" + "="*60)
        print("Browser will stay open for 60 seconds...")
        print("="*60)
        await page.wait_for_timeout(60000)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_drugbank_add_drugs())
