#!/usr/bin/env python3
"""
Playwright-based Drug-Drug Interaction (DDI) Scraper for drugs.com
Reads drug pairs from Excel and checks interactions on drugs.com
"""

import asyncio
import time
import logging
import random
from datetime import datetime
from pathlib import Path
import pandas as pd
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('playwright_ddi_scraper.log'),
        logging.StreamHandler()
    ]
)


class PlaywrightDDIScraper:
    """Scraper for checking drug interactions on drugs.com using Playwright"""

    def __init__(self, headless=True, delay_between_requests=3.5):
        """
        Initialize the scraper

        Args:
            headless: Run browser in headless mode
            delay_between_requests: Delay in seconds between drug pair checks (minimum 3 seconds)
        """
        self.headless = headless
        self.delay_between_requests = max(delay_between_requests, 3.0)  # Ensure minimum 3 seconds
        self.browser = None
        self.context = None
        self.page = None

    async def initialize(self):
        """Initialize Playwright browser"""
        logging.info("Initializing Playwright browser...")
        playwright = await async_playwright().start()

        # Launch browser with stealth options
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--lang=en-US,en'
            ]
        )

        # Create context with realistic settings
        self.context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation'],
            color_scheme='light',
            device_scale_factor=1,
            has_touch=False,
            is_mobile=False,
            java_script_enabled=True
        )

        # Create page
        self.page = await self.context.new_page()

        # Add extra headers to appear more realistic
        await self.page.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })

        # Inject scripts to mask automation
        await self.page.add_init_script("""
            // Overwrite the `plugins` property to use a custom getter
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // Overwrite the `languages` property to use a custom getter
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });

            // Overwrite the `plugins` property
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            // Pass chrome check
            window.chrome = {
                runtime: {}
            };

            // Pass permissions check
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)

        logging.info("Browser initialized successfully with anti-detection measures")

    async def check_interaction(self, drug1, drug2):
        """
        Check drug-drug interaction for a pair of drugs

        Args:
            drug1: First drug name
            drug2: Second drug name

        Returns:
            dict: Contains drug1, drug2, severity, and status
        """
        logging.info(f"Checking interaction: {drug1} + {drug2}")

        result = {
            'Drug1': drug1,
            'Drug2': drug2,
            'DDI_Severity': 'Error',
            'Status': 'Failed',
            'Error_Message': None,
            'Check_Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        try:
            # First visit homepage to establish session (more human-like)
            homepage_url = "https://www.drugs.com/"
            logging.debug(f"Visiting homepage first: {homepage_url}")
            try:
                await self.page.goto(homepage_url, wait_until='load', timeout=30000)
                await asyncio.sleep(2)  # Human-like delay
            except Exception as e:
                logging.warning(f"Could not load homepage, trying direct navigation: {e}")

            # Navigate to the drug interaction checker
            url = "https://www.drugs.com/interaction/list/"
            logging.debug(f"Navigating to {url}")
            # Use 'load' instead of 'networkidle' to avoid waiting for all network activity
            await self.page.goto(url, wait_until='load', timeout=30000)

            # Wait a bit for page to fully load (human-like behavior)
            await asyncio.sleep(2)

            # Add first drug
            logging.debug(f"Adding first drug: {drug1}")
            await self._add_drug(drug1)

            # Random delay between adding drugs (human-like)
            await asyncio.sleep(random.uniform(1.5, 2.5))

            # Add second drug
            logging.debug(f"Adding second drug: {drug2}")
            await self._add_drug(drug2)

            # Random delay before clicking check button (human-like)
            await asyncio.sleep(random.uniform(1.0, 2.0))

            # Click the "Check Interactions" button
            logging.debug("Clicking check interactions button")
            check_button_selector = "#interaction_list > div > a"
            await self.page.wait_for_selector(check_button_selector, timeout=5000)
            await self.page.click(check_button_selector)

            # Wait for results page to load
            await asyncio.sleep(2)
            await self.page.wait_for_load_state('load', timeout=15000)
            await asyncio.sleep(1)  # Additional wait for dynamic content

            # Extract the DDI severity
            severity = await self._extract_severity()

            result['DDI_Severity'] = severity
            result['Status'] = 'Success'
            result['Error_Message'] = None

            logging.info(f"Result: {drug1} + {drug2} = {severity}")

        except PlaywrightTimeoutError as e:
            error_msg = f"Timeout error: {str(e)}"
            logging.error(f"Timeout checking {drug1} + {drug2}: {error_msg}")
            result['Error_Message'] = error_msg
            result['DDI_Severity'] = 'Timeout'

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            logging.error(f"Error checking {drug1} + {drug2}: {error_msg}")
            result['Error_Message'] = error_msg
            result['DDI_Severity'] = 'Error'

        return result

    async def _add_drug(self, drug_name):
        """
        Add a drug to the interaction checker

        Args:
            drug_name: Name of the drug to add
        """
        try:
            # Wait for the search input to be visible
            search_input_selector = "#livesearch-interaction"
            await self.page.wait_for_selector(search_input_selector, timeout=5000)

            # Clear any existing text with human-like delay
            await self.page.fill(search_input_selector, "")
            await asyncio.sleep(random.uniform(0.3, 0.6))

            # Type the drug name character by character (more human-like)
            await self.page.type(search_input_selector, drug_name, delay=random.randint(50, 150))

            # Wait for autocomplete suggestions to appear (random delay)
            await asyncio.sleep(random.uniform(1.5, 2.0))

            # Try to select from autocomplete first (more reliable)
            try:
                # Look for autocomplete suggestion matching the drug name
                autocomplete_item = f"//div[@id='livesearch-interaction-ac']//b[contains(text(), '{drug_name[:5]}')]"
                autocomplete_element = await self.page.wait_for_selector(autocomplete_item, timeout=2000)
                if autocomplete_element:
                    await autocomplete_element.click()
                    await asyncio.sleep(random.uniform(0.5, 0.8))
                    return  # Drug added via autocomplete
            except Exception:
                # Autocomplete not found, continue with button click
                logging.debug(f"Autocomplete not found for {drug_name}, using button instead")
                pass

            # If autocomplete didn't work, use the add button
            add_button_selector = "#drug-interactions-search > div > button"
            await self.page.wait_for_selector(add_button_selector, timeout=5000)

            # Use force click to bypass any overlays
            await self.page.click(add_button_selector, force=True)

            # Wait for the drug to be added (random delay)
            await asyncio.sleep(random.uniform(0.5, 1.0))

        except Exception as e:
            logging.warning(f"Error adding drug {drug_name}: {str(e)}")
            raise

    async def _extract_severity(self):
        """
        Extract DDI severity from the results page

        Returns:
            str: Severity level (Minor, Moderate, Major, or N/A)
        """
        try:
            # Try multiple possible selectors for severity
            severity_selectors = [
                "#content > div:nth-child(9) > div > div > span",
                "#content > div > div > div > span",
                "span.ddc-alert-level",
                ".ddc-alert-level",
                "span[class*='alert']"
            ]

            for selector in severity_selectors:
                try:
                    # Check if element exists
                    element = await self.page.query_selector(selector)
                    if element:
                        severity_text = await element.inner_text()
                        severity_text = severity_text.strip()

                        # Check if it's a valid severity level
                        if any(level in severity_text.upper() for level in ['MINOR', 'MODERATE', 'MAJOR']):
                            # Extract just the severity level
                            for level in ['Minor', 'Moderate', 'Major']:
                                if level.upper() in severity_text.upper():
                                    logging.debug(f"Found severity: {level}")
                                    return level

                except Exception:
                    continue

            # Check if "No interactions found" message is present
            page_content = await self.page.content()

            if any(phrase in page_content.lower() for phrase in [
                'no interactions found',
                'no known interaction',
                'no results found',
                'did not match any'
            ]):
                logging.debug("No interaction found")
                return "N/A"

            # If we couldn't find severity, log page content for debugging
            logging.warning("Could not find severity indicator on page")

            # Try to extract from page title or headers
            try:
                title = await self.page.title()
                if "interaction" in title.lower():
                    for level in ['Minor', 'Moderate', 'Major']:
                        if level.lower() in title.lower():
                            return level
            except Exception:
                pass

            return "Unknown"

        except Exception as e:
            logging.error(f"Error extracting severity: {str(e)}")
            return "Error"

    async def close(self):
        """Close the browser"""
        if self.browser:
            await self.browser.close()
            logging.info("Browser closed")


async def process_drug_pairs(input_file, output_file=None, checkpoint_file="ddi_checkpoint.csv"):
    """
    Process drug pairs from Excel file and check interactions

    Args:
        input_file: Path to Excel file with Drug1 and Drug2 columns
        output_file: Path to save results (defaults to input_file)
        checkpoint_file: Path to checkpoint file for saving progress
    """
    # Read the Excel file
    logging.info(f"Reading drug pairs from: {input_file}")

    try:
        df = pd.read_excel(input_file)
    except Exception as e:
        logging.error(f"Error reading Excel file: {e}")
        return

    # Validate columns
    if 'Drug1' not in df.columns or 'Drug2' not in df.columns:
        logging.error("Excel file must contain 'Drug1' and 'Drug2' columns")
        logging.info(f"Found columns: {df.columns.tolist()}")
        return

    # Add DDI_Severity column if it doesn't exist
    if 'DDI_Severity' not in df.columns:
        df['DDI_Severity'] = None

    # Set output file
    if output_file is None:
        output_file = input_file

    # Load checkpoint if it exists
    start_index = 0
    if Path(checkpoint_file).exists():
        try:
            checkpoint_df = pd.read_csv(checkpoint_file)
            # Find the last successfully processed row
            completed_rows = checkpoint_df[checkpoint_df['Status'] == 'Success']
            if not completed_rows.empty:
                start_index = len(completed_rows)
                logging.info(f"Resuming from checkpoint. Already processed {start_index} drug pairs")

                # Update df with checkpoint data
                for idx, row in checkpoint_df.iterrows():
                    if idx < len(df):
                        df.at[idx, 'DDI_Severity'] = row['DDI_Severity']
        except Exception as e:
            logging.warning(f"Could not load checkpoint: {e}")

    # Initialize scraper
    scraper = PlaywrightDDIScraper(headless=True, delay_between_requests=3.5)
    await scraper.initialize()

    try:
        total_pairs = len(df)
        logging.info(f"Processing {total_pairs - start_index} drug pairs (starting from index {start_index})")

        # Process each drug pair
        for idx in range(start_index, total_pairs):
            row = df.iloc[idx]
            drug1 = str(row['Drug1']).strip()
            drug2 = str(row['Drug2']).strip()

            # Skip if already processed
            if pd.notna(df.at[idx, 'DDI_Severity']) and df.at[idx, 'DDI_Severity'] not in ['Error', 'Timeout']:
                logging.info(f"[{idx+1}/{total_pairs}] Skipping {drug1} + {drug2} (already processed)")
                continue

            logging.info(f"\n{'='*60}")
            logging.info(f"Progress: {idx+1}/{total_pairs} ({(idx+1)/total_pairs*100:.1f}%)")
            logging.info(f"{'='*60}")

            # Check interaction
            result = await scraper.check_interaction(drug1, drug2)

            # Update dataframe
            df.at[idx, 'DDI_Severity'] = result['DDI_Severity']

            # Save progress after each drug pair
            df.to_excel(output_file, index=False)
            logging.info(f"Progress saved to {output_file}")

            # Save checkpoint
            checkpoint_data = df[['Drug1', 'Drug2', 'DDI_Severity']].copy()
            checkpoint_data['Status'] = checkpoint_data['DDI_Severity'].apply(
                lambda x: 'Success' if x not in ['Error', 'Timeout', None] else 'Failed'
            )
            checkpoint_data['Check_Timestamp'] = result['Check_Timestamp']
            checkpoint_data.to_csv(checkpoint_file, index=False)

            # Rate limiting - wait between requests with randomization
            if idx < total_pairs - 1:  # Don't wait after the last pair
                # Add random variation to delay (±1 second) to appear more human
                random_delay = scraper.delay_between_requests + random.uniform(-1.0, 1.0)
                random_delay = max(random_delay, 3.0)  # Ensure minimum 3 seconds
                logging.info(f"Waiting {random_delay:.1f} seconds before next request...")
                await asyncio.sleep(random_delay)

        # Final save
        df.to_excel(output_file, index=False)

        # Print summary
        logging.info(f"\n{'='*60}")
        logging.info("SCRAPING COMPLETE!")
        logging.info(f"{'='*60}")
        logging.info(f"Total drug pairs processed: {total_pairs}")

        # Count severities
        severity_counts = df['DDI_Severity'].value_counts()
        logging.info("\nSeverity Distribution:")
        for severity, count in severity_counts.items():
            logging.info(f"  {severity}: {count}")

        logging.info(f"\nResults saved to: {output_file}")
        logging.info(f"{'='*60}")

    except KeyboardInterrupt:
        logging.warning("\nScraping interrupted by user")
        df.to_excel(output_file, index=False)
        logging.info(f"Progress saved to {output_file}")

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await scraper.close()


async def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description='Check drug-drug interactions using Playwright')
    parser.add_argument('input_file', help='Excel file with Drug1 and Drug2 columns')
    parser.add_argument('--output', '-o', help='Output Excel file (defaults to input file)')
    parser.add_argument('--checkpoint', '-c', default='ddi_checkpoint.csv',
                       help='Checkpoint file for progress tracking')
    parser.add_argument('--delay', '-d', type=float, default=3.5,
                       help='Delay between requests in seconds (minimum 3.0)')

    args = parser.parse_args()

    # Validate input file exists
    if not Path(args.input_file).exists():
        logging.error(f"Input file not found: {args.input_file}")
        return

    await process_drug_pairs(args.input_file, args.output, args.checkpoint)


if __name__ == "__main__":
    asyncio.run(main())
