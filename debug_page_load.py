#!/usr/bin/env python3
"""
Debug script to inspect the drug interactions page and check element visibility
"""
import asyncio
from playwright.async_api import async_playwright

async def debug_page():
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
        print("Navigating to drug interactions page...")
        print("=" * 60)

        # Navigate to the page
        await page.goto("https://www.drugs.com/drug_interactions.html", wait_until='load', timeout=30000)

        # Wait a bit for any dynamic content
        print("Waiting 3 seconds for page to settle...")
        await page.wait_for_timeout(3000)

        # Take screenshot
        await page.screenshot(path='debug_page_state.png', full_page=True)
        print("✓ Screenshot saved: debug_page_state.png")

        # Save HTML
        html = await page.content()
        with open('debug_page_state.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("✓ HTML saved: debug_page_state.html")

        print("\n" + "=" * 60)
        print("Checking for key elements...")
        print("=" * 60)

        # Check for search input
        search_input = await page.query_selector("#livesearch-interaction-basic")
        print(f"Search input (#livesearch-interaction-basic): {'✓ FOUND' if search_input else '✗ NOT FOUND'}")

        # Check for the add button with the selector we're using
        add_button = await page.query_selector("#drug-interactions-search > div > button")
        print(f"Add button (#drug-interactions-search > div > button): {'✓ FOUND' if add_button else '✗ NOT FOUND'}")

        # Try alternative selectors for add button
        print("\n--- Trying alternative add button selectors ---")
        alt_selectors = [
            "#drug-interactions-search button",
            "button[type='button']",
            ".btn-add",
            "button.ddc-btn",
        ]

        for selector in alt_selectors:
            element = await page.query_selector(selector)
            if element:
                text = await element.inner_text()
                print(f"  ✓ {selector}: '{text}'")

        # List all buttons on the page
        print("\n--- All buttons on the page ---")
        buttons = await page.query_selector_all("button")
        for i, btn in enumerate(buttons):
            try:
                btn_id = await btn.get_attribute('id') or '(no id)'
                btn_class = await btn.get_attribute('class') or '(no class)'
                btn_text = await btn.inner_text()
                btn_type = await btn.get_attribute('type') or '(no type)'
                print(f"  Button {i+1}: id='{btn_id}', class='{btn_class}', type='{btn_type}', text='{btn_text.strip()[:50]}'")
            except:
                print(f"  Button {i+1}: (error reading attributes)")

        # Check the structure of #drug-interactions-search
        print("\n--- Structure of #drug-interactions-search ---")
        search_section = await page.query_selector("#drug-interactions-search")
        if search_section:
            section_html = await search_section.inner_html()
            print(section_html[:1000])  # Print first 1000 chars
        else:
            print("✗ #drug-interactions-search NOT FOUND")

        # Check for interaction list
        print("\n--- Checking #interaction_list ---")
        interaction_list = await page.query_selector("#interaction_list")
        print(f"Interaction list (#interaction_list): {'✓ FOUND' if interaction_list else '✗ NOT FOUND'}")

        # Keep browser open for inspection
        print("\n" + "=" * 60)
        print("Browser will stay open for 30 seconds for manual inspection...")
        print("=" * 60)
        await page.wait_for_timeout(30000)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_page())
