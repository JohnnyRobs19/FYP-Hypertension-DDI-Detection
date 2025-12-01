#!/usr/bin/env python3
"""
Debug script to add drugs and see the structure of the interaction list
"""
import asyncio
from playwright.async_api import async_playwright

async def debug_add_drugs():
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

        print("Navigating to drug interactions page...")
        await page.goto("https://www.drugs.com/drug_interactions.html", wait_until='load')
        await page.wait_for_timeout(2000)

        # Take screenshot of initial state
        await page.screenshot(path='debug_1_initial.png')
        print("✓ Initial state screenshot saved")

        # Add first drug
        print("\n--- Adding first drug: Lisinopril ---")
        search_input = "#livesearch-interaction-basic"
        await page.fill(search_input, "Lisinopril")
        await page.wait_for_timeout(1000)

        # Click the Add button using corrected selector
        add_button = ".interactions-search button[type='submit']"
        await page.click(add_button)
        print("✓ Clicked Add button for Lisinopril")
        await page.wait_for_timeout(2000)

        # Take screenshot after adding first drug
        await page.screenshot(path='debug_2_after_first_drug.png')
        print("✓ Screenshot after first drug saved")

        # Check what elements exist now
        print("\n--- Checking for interaction list elements ---")

        # Save HTML
        html = await page.content()
        with open('debug_after_first_drug.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("✓ HTML saved: debug_after_first_drug.html")

        # Add second drug
        print("\n--- Adding second drug: Amlodipine ---")
        await page.fill(search_input, "Amlodipine")
        await page.wait_for_timeout(1000)
        await page.click(add_button)
        print("✓ Clicked Add button for Amlodipine")
        await page.wait_for_timeout(2000)

        # Take screenshot after adding second drug
        await page.screenshot(path='debug_3_after_second_drug.png')
        print("✓ Screenshot after second drug saved")

        # Save HTML after second drug
        html = await page.content()
        with open('debug_after_second_drug.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("✓ HTML saved: debug_after_second_drug.html")

        # Now check for the "Check Interactions" button
        print("\n--- Looking for 'Check Interactions' button ---")
        check_selectors = [
            "#interaction_list > div > a",
            "#interaction_list a",
            "a.ddc-btn",
            "a[href*='interaction']",
        ]

        for selector in check_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.inner_text()
                    href = await element.get_attribute('href')
                    print(f"  ✓ {selector}: text='{text}', href='{href}'")
            except:
                print(f"  ✗ {selector}: NOT FOUND")

        # List all links on page
        print("\n--- All links (anchors) on the page ---")
        links = await page.query_selector_all("a")
        for i, link in enumerate(links[:20]):  # First 20 links
            try:
                text = await link.inner_text()
                href = await link.get_attribute('href') or ''
                if text.strip() and ('interaction' in href.lower() or 'check' in text.lower()):
                    print(f"  Link {i}: text='{text.strip()[:50]}', href='{href[:80]}'")
            except:
                pass

        # Keep browser open
        print("\n" + "="*60)
        print("Browser will stay open for 30 seconds...")
        print("="*60)
        await page.wait_for_timeout(30000)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_add_drugs())
