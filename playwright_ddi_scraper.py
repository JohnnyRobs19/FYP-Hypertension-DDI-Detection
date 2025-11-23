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

            # Verify that both drugs were added to the list
            await asyncio.sleep(random.uniform(0.5, 1.0))
            logging.debug("Verifying drugs were added to the list")
            try:
                # Check if the interaction list has drugs
                interaction_list = await self.page.query_selector("#interaction_list")
                if interaction_list:
                    list_content = await interaction_list.inner_text()
                    logging.debug(f"Interaction list content: {list_content}")

                    # Verify at least some drugs are in the list
                    if not list_content or len(list_content.strip()) < 5:
                        logging.warning("Interaction list appears empty. Drugs may not have been added properly.")
                else:
                    logging.warning("Could not find interaction list element")
            except Exception as e:
                logging.warning(f"Could not verify drug list: {e}")

            # Random delay before clicking check button (human-like)
            await asyncio.sleep(random.uniform(1.0, 2.0))

            # Click the "Check Interactions" button
            logging.debug("Clicking check interactions button")

            # Try multiple selectors for the check button
            check_button_selectors = [
                "#interaction_list > div > a",
                "#interaction_list a",
                "a.ddc-btn.ddc-btn-default",
                "a[href*='interactions-between']",
                "//a[contains(text(), 'Check Interactions')]"
            ]

            button_clicked = False
            for selector in check_button_selectors:
                try:
                    logging.debug(f"Trying selector: {selector}")
                    # Check if it's an XPath selector
                    if selector.startswith('//'):
                        await self.page.wait_for_selector(f"xpath={selector}", state='visible', timeout=15000)
                        await self.page.click(f"xpath={selector}")
                    else:
                        await self.page.wait_for_selector(selector, state='visible', timeout=15000)
                        await self.page.click(selector)
                    button_clicked = True
                    logging.debug(f"Successfully clicked button with selector: {selector}")
                    break
                except Exception as e:
                    logging.debug(f"Selector {selector} failed: {str(e)}")
                    continue

            if not button_clicked:
                # Save screenshot for debugging
                screenshot_path = f"error_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await self.page.screenshot(path=screenshot_path)
                logging.error(f"Screenshot saved to {screenshot_path} for debugging")

                # Also save the page HTML for inspection
                html_path = f"error_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                page_content = await self.page.content()
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(page_content)
                logging.error(f"Page HTML saved to {html_path} for debugging")

                raise Exception("Could not find or click the 'Check Interactions' button with any known selector")

            # Wait for results page to load
            await asyncio.sleep(2)
            await self.page.wait_for_load_state('load', timeout=30000)  # Increased from 15s to 30s

            # CRITICAL: Wait for the interaction results to be rendered
            # The page loads dynamic content after the 'load' event
            logging.info("Waiting for interaction results to render...")
            try:
                # Wait specifically for the "Interactions between your drugs" heading
                await self.page.wait_for_selector('h2:has-text("Interactions between your drugs")', timeout=10000)
                logging.info("Found 'Interactions between your drugs' heading")
                # Additional wait for content to fully render
                await asyncio.sleep(2)
            except Exception as e:
                logging.warning(f"Timeout waiting for interaction heading: {e}")
                # Continue anyway, might still find content

            # Extract the DDI severity
            severity = await self._extract_severity()

            result['DDI_Severity'] = severity

            # Set status based on severity result
            if severity in ['Error', 'NA']:
                result['Status'] = 'Completed with issues'
            else:
                result['Status'] = 'Success'

            result['Error_Message'] = None

            # Log with appropriate level based on result
            if severity == 'Error':
                logging.warning(f"Result: {drug1} + {drug2} = {severity} (extraction error)")
            elif severity == 'NA':
                logging.warning(f"Result: {drug1} + {drug2} = {severity} (could not determine)")
            else:
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
        Extract DDI severity from the results page using proper logic:
        1. FIRST check for "No drug ⬌ drug interactions were found" message in specific div
        2. If no interaction message exists, THEN look for severity labels ONLY in drug-drug interaction section
        3. Return 'NA' if none found

        Returns:
            str: Severity level (Major, Moderate, Minor, No interaction, or NA)
        """
        try:
            # STEP 1: CRITICAL - Check for "No interaction" message FIRST
            # This specific div appears when there are no drug-drug interactions
            logging.debug("STEP 1: Checking for 'No interaction' message...")

            try:
                no_interaction_selector = "div.interactions-reference-wrapper"
                no_interaction_element = await self.page.query_selector(no_interaction_selector)

                if no_interaction_element:
                    element_text = await no_interaction_element.inner_text()
                    logging.debug(f"Found interactions-reference-wrapper with text: {element_text[:100]}...")

                    # Check for the specific "No drug ⬌ drug interactions" message
                    if "No drug" in element_text and "drug interactions were found" in element_text:
                        logging.info("Found 'No drug ⬌ drug interactions were found' message - returning 'No interaction'")
                        return "No interaction"
            except Exception as e:
                logging.debug(f"Error checking for no-interaction div: {e}")

            # STEP 2: Find the "Interactions between your drugs" section and its wrapper
            logging.info("STEP 2: Looking for drug-drug interaction section...")

            interaction_wrapper = None

            # Strategy: Use XPath to find the div immediately after the h2 heading
            # This is more reliable than traversing from heading element
            try:
                xpath_selector = 'xpath=//h2[contains(text(), "Interactions between your drugs")]/following-sibling::div[1]'
                interaction_wrapper = await self.page.query_selector(xpath_selector)

                if interaction_wrapper:
                    # Verify it's the right wrapper by checking its class
                    wrapper_class = await interaction_wrapper.get_attribute('class') or ''
                    logging.info(f"Found interaction wrapper with XPath (class: {wrapper_class})")
                else:
                    logging.warning("XPath did not find wrapper element")
            except Exception as e:
                logging.warning(f"XPath wrapper selection failed: {e}")

            # Fallback: Try CSS selector if XPath failed
            if not interaction_wrapper:
                logging.info("Trying CSS selector fallback for wrapper...")
                try:
                    # This will find the first div.interactions-reference-wrapper
                    # which should be the drug-drug interaction section
                    interaction_wrapper = await self.page.query_selector("div.interactions-reference-wrapper")
                    if interaction_wrapper:
                        logging.info("Found wrapper with CSS selector")
                    else:
                        logging.warning("CSS selector did not find wrapper")
                except Exception as e:
                    logging.warning(f"CSS selector failed: {e}")

            if not interaction_wrapper:
                logging.warning("Could not find interaction wrapper with any method")
                await self._save_debug_info("no_wrapper_found")
                return "NA"

            # STEP 3: Look for severity labels ONLY within the drug-drug interaction section
            logging.info("STEP 3: Searching for severity label...")

            # Look for severity label ONLY in the interaction wrapper (not globally!)
            severity_selector = "span.ddc-status-label"

            try:
                # Search within interaction_wrapper for the severity label
                severity_element = await interaction_wrapper.query_selector(severity_selector)

                if severity_element:
                    element_class = await severity_element.get_attribute("class") or ""
                    element_text = await severity_element.inner_text()
                    logging.info(f"Found severity element - class: {element_class}, text: '{element_text}'")

                    # Check class for severity category
                    if "status-category-major" in element_class:
                        logging.info("✓ Extracted severity: Major")
                        return "Major"
                    elif "status-category-moderate" in element_class:
                        logging.info("✓ Extracted severity: Moderate")
                        return "Moderate"
                    elif "status-category-minor" in element_class:
                        logging.info("✓ Extracted severity: Minor")
                        return "Minor"

                    # Fallback: check text content
                    element_text_upper = element_text.strip().upper()
                    if element_text_upper in ["MAJOR", "MODERATE", "MINOR"]:
                        severity_found = element_text.strip().capitalize()
                        logging.info(f"✓ Extracted severity via text: {severity_found}")
                        return severity_found

                    logging.warning(f"Found severity element but couldn't determine severity from class or text")
                else:
                    logging.warning("No span.ddc-status-label found in interaction wrapper")

            except Exception as e:
                logging.warning(f"Error finding severity label: {e}")
                import traceback
                logging.debug(traceback.format_exc())

            # STEP 4: If we have the wrapper but no severity label, check HTML content within wrapper only
            if interaction_wrapper:
                logging.debug("STEP 4: Checking HTML content within wrapper for severity labels...")
                try:
                    wrapper_content = await interaction_wrapper.inner_html()
                    content_lower = wrapper_content.lower()

                    # Check for severity in specific order (Major first as it's most important)
                    if 'status-category-major' in content_lower and 'ddc-status-label' in content_lower:
                        logging.info("Found Major severity in wrapper HTML (Method: HTML class detection)")
                        return "Major"

                    if 'status-category-moderate' in content_lower and 'ddc-status-label' in content_lower:
                        logging.info("Found Moderate severity in wrapper HTML (Method: HTML class detection)")
                        return "Moderate"

                    if 'status-category-minor' in content_lower and 'ddc-status-label' in content_lower:
                        logging.info("Found Minor severity in wrapper HTML (Method: HTML class detection)")
                        return "Minor"
                except Exception as e:
                    logging.debug(f"Error checking wrapper HTML: {e}")

            # STEP 4.5: NEW FALLBACK - Try broader badge/span detection within interaction section
            if interaction_wrapper:
                logging.debug("STEP 4.5: Trying broader badge/span detection for severity...")
                try:
                    # Try multiple selector strategies for finding severity badges
                    badge_selectors = [
                        "span",  # All spans within wrapper
                        "div > span",  # Direct child spans
                        "[class*='severity']",  # Elements with 'severity' in class
                        "[class*='badge']",  # Elements with 'badge' in class
                        "[class*='label']",  # Elements with 'label' in class
                        "[class*='interaction']",  # Elements with 'interaction' in class
                        "[class*='moderate']",  # Elements with severity level in class
                        "[class*='major']",
                        "[class*='minor']"
                    ]

                    for selector in badge_selectors:
                        try:
                            elements = await interaction_wrapper.query_selector_all(selector)
                            logging.debug(f"  Checking {len(elements)} elements with selector: {selector}")

                            for element in elements:
                                try:
                                    element_text = await element.inner_text()
                                    element_text_clean = element_text.strip().upper()

                                    # Check if text matches severity levels
                                    if element_text_clean in ["MAJOR", "MODERATE", "MINOR"]:
                                        # Get element class for additional context
                                        element_class = await element.get_attribute("class") or ""
                                        logging.info(f"Found {element_text_clean.capitalize()} severity badge (Method: Badge text detection)")
                                        logging.debug(f"  Element selector: {selector}, class: {element_class}, text: {element_text_clean}")
                                        return element_text_clean.capitalize()

                                    # Also check if the text contains the severity word (e.g., "Severity: Moderate")
                                    for severity in ["MAJOR", "MODERATE", "MINOR"]:
                                        if severity in element_text_clean:
                                            logging.info(f"Found {severity.capitalize()} severity in element text (Method: Badge text contains detection)")
                                            logging.debug(f"  Element selector: {selector}, text: {element_text_clean}")
                                            return severity.capitalize()

                                except Exception as elem_error:
                                    logging.debug(f"  Error processing element: {elem_error}")
                                    continue

                        except Exception as selector_error:
                            logging.debug(f"  Error with selector {selector}: {selector_error}")
                            continue

                    logging.debug("Badge/span detection completed - no severity found")

                except Exception as e:
                    logging.debug(f"Error in badge detection fallback: {e}")

            # STEP 4.6: Try searching for specific CSS selector pattern from user's hint
            # #content > div:nth-child(9) > div > div > span
            if interaction_wrapper:
                logging.debug("STEP 4.6: Trying specific nested div > span pattern...")
                try:
                    # Try to find nested divs with spans that might contain severity
                    nested_spans = await interaction_wrapper.query_selector_all("div > div > span")
                    logging.debug(f"  Found {len(nested_spans)} nested div > div > span elements")

                    for span in nested_spans:
                        try:
                            span_text = await span.inner_text()
                            span_text_clean = span_text.strip().upper()
                            span_class = await span.get_attribute("class") or ""

                            # Check for severity text
                            if span_text_clean in ["MAJOR", "MODERATE", "MINOR"]:
                                logging.info(f"Found {span_text_clean.capitalize()} severity (Method: Nested span detection)")
                                logging.debug(f"  Span class: {span_class}, text: {span_text_clean}")
                                return span_text_clean.capitalize()

                            # Check if class name hints at severity
                            class_lower = span_class.lower()
                            if any(severity_hint in class_lower for severity_hint in ['major', 'moderate', 'minor', 'severity']):
                                for severity in ["MAJOR", "MODERATE", "MINOR"]:
                                    if severity.lower() in class_lower or severity in span_text_clean:
                                        logging.info(f"Found {severity.capitalize()} severity (Method: Span class analysis)")
                                        logging.debug(f"  Span class: {span_class}, text: {span_text_clean}")
                                        return severity.capitalize()

                        except Exception as span_error:
                            logging.debug(f"  Error processing nested span: {span_error}")
                            continue

                except Exception as e:
                    logging.debug(f"Error in nested span detection: {e}")

            # STEP 5: If none found, return NA
            logging.warning("Could not determine severity - no matching patterns found in drug-drug interaction section")
            await self._save_debug_info("no_severity_found")
            return "NA"

        except Exception as e:
            logging.error(f"Error extracting severity: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            await self._save_debug_info("extraction_error")
            return "Error"

    async def _save_debug_info(self, reason="debug"):
        """Save screenshot and HTML for debugging purposes"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Save screenshot
            screenshot_path = f"debug_screenshot_{reason}_{timestamp}.png"
            await self.page.screenshot(path=screenshot_path, full_page=True)
            logging.info(f"Debug screenshot saved to {screenshot_path}")

            # Save HTML
            html_path = f"debug_page_{reason}_{timestamp}.html"
            page_content = await self.page.content()
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(page_content)
            logging.info(f"Debug HTML saved to {html_path}")

        except Exception as e:
            logging.error(f"Could not save debug info: {e}")

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

    # Add DDI_Severity column if it doesn't exist, or ensure it's object dtype
    if 'DDI_Severity' not in df.columns:
        df['DDI_Severity'] = pd.Series(dtype='object')  # Explicitly set to object dtype to avoid dtype warnings
    else:
        # Ensure the column is object dtype even if it exists
        df['DDI_Severity'] = df['DDI_Severity'].astype('object')

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
