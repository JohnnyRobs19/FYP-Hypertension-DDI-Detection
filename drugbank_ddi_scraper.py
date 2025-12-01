#!/usr/bin/env python3
"""
Playwright-based Drug-Drug Interaction (DDI) Scraper for DrugBank
Reads drug pairs from CSV and checks interactions on dev.drugbank.com/demo/ddi_checker
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
        logging.FileHandler('drugbank_scraper.log'),
        logging.StreamHandler()
    ]
)


class DrugBankDDIScraper:
    """Scraper for checking drug interactions on DrugBank DDI Checker using Playwright"""

    def __init__(self, headless=False, delay_between_requests=2.5):
        """
        Initialize the scraper

        Args:
            headless: Run browser in headless mode (False to see it working)
            delay_between_requests: Delay in seconds between drug pair checks
        """
        self.headless = headless
        self.delay_between_requests = max(delay_between_requests, 2.0)
        self.browser = None
        self.context = None
        self.page = None

        # Selectors based on user specifications
        self.input_selector = "#vs1__combobox > div.vs__selected-options > input"
        self.check_button_selector = "body > main > div.panel.plugin-panel > div > div.demo-body > div > div.panel-right.col-right.col-xs-12.col-sm-8 > div > div.row.ddi-controls > center > a.button.dark.check-interactions"
        self.result_container_selector = "div > div > div.ddi-widget-body > div > div.form-row.mb-3"
        self.severity_selector = "div > div > div.ddi-widget-body > div > div.form-row.mb-3 > div > div > div.card-row.header-row > div.intx-item.interaction-severity > div > h5"
        self.description_selector = "div > div > div.ddi-widget-body > div > div.form-row.mb-3 > div > div > div:nth-child(2)"

    async def initialize(self):
        """Initialize Playwright browser with anti-detection measures"""
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
            // Overwrite the `webdriver` property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // Overwrite the `languages` property
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
            dict: Contains drug1, drug2, severity, text, and status
        """
        logging.info(f"Checking interaction: {drug1} + {drug2}")

        result = {
            'Drug1': drug1,
            'Drug2': drug2,
            'DrugBank_Severity': 'Error',
            'DrugBank_Text': 'Error extracting interaction information',
            'Status': 'Failed',
            'Error_Message': None,
            'Check_Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        try:
            # Navigate to the DrugBank DDI Checker
            url = "https://dev.drugbank.com/demo/ddi_checker"
            logging.debug(f"Navigating to {url}")
            await self.page.goto(url, wait_until='load', timeout=30000)

            # Wait for page to fully load
            await self.page.wait_for_timeout(2000)

            # Add first drug
            logging.debug(f"Adding first drug: {drug1}")
            await self._add_drug(drug1)

            # Random delay between adding drugs (human-like)
            await self.page.wait_for_timeout(random.randint(1500, 2500))

            # Add second drug
            logging.debug(f"Adding second drug: {drug2}")
            await self._add_drug(drug2)

            # Random delay before clicking check button
            delay = random.randint(1000, 2000)
            logging.debug(f"Waiting {delay/1000:.1f} seconds before clicking Check Interactions button...")
            await self.page.wait_for_timeout(delay)

            # Click the "Check Interactions" button
            logging.info("Clicking 'Check Interactions' button...")
            try:
                await self._click_check_button()
            except Exception as e:
                logging.error(f"Could not click Check Interactions button: {str(e)}")
                await self._save_debug_info(f"button_click_error_{drug1}_{drug2}")
                raise Exception(f"Could not find or click the 'Check Interactions' button: {str(e)}")

            # Wait for results to load
            logging.info("Waiting for interaction results to load...")
            await self.page.wait_for_timeout(3000)
            await self.page.wait_for_load_state('load', timeout=30000)

            # Additional wait for dynamic content
            await self.page.wait_for_timeout(2000)

            # Extract severity and text
            severity, interaction_text = await self._extract_severity_and_text(drug1, drug2)

            result['DrugBank_Severity'] = severity
            result['DrugBank_Text'] = interaction_text

            # Set status based on severity result
            if severity == 'Error':
                result['Status'] = 'Failed'
            elif severity in ['None', 'Major', 'Moderate', 'Minor']:
                result['Status'] = 'Success'
            else:
                result['Status'] = 'Completed with issues'

            result['Error_Message'] = None

            # Log with appropriate level based on result
            if severity == 'Error':
                logging.warning(f"Result: {drug1} + {drug2} = {severity} (extraction error)")
            elif severity == 'None':
                logging.info(f"Result: {drug1} + {drug2} = {severity} (no interaction found)")
            else:
                logging.info(f"Result: {drug1} + {drug2} = {severity}")
                logging.debug(f"Interaction text: {interaction_text[:100]}...")

        except PlaywrightTimeoutError as e:
            error_msg = f"Timeout error: {str(e)}"
            logging.error(f"Timeout checking {drug1} + {drug2}: {error_msg}")
            result['Error_Message'] = error_msg
            result['DrugBank_Severity'] = 'Timeout'
            result['DrugBank_Text'] = 'Request timed out'

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            logging.error(f"Error checking {drug1} + {drug2}: {error_msg}")
            result['Error_Message'] = error_msg
            result['DrugBank_Severity'] = 'Error'
            result['DrugBank_Text'] = f'Error: {str(e)}'

        return result

    async def _add_drug(self, drug_name):
        """
        Add a drug to the interaction checker with smart dropdown selection

        Args:
            drug_name: Name of the drug to add
        """
        try:
            # Wait for input field to be visible
            await self.page.wait_for_selector(self.input_selector, state='visible', timeout=10000)

            # Clear the input field
            await self.page.fill(self.input_selector, "")
            await self.page.wait_for_timeout(500)

            # Type the drug name character by character (human-like)
            logging.info(f"Typing drug name: {drug_name}")
            await self.page.type(self.input_selector, drug_name, delay=random.randint(50, 150))

            # Wait for dropdown to appear
            logging.debug("Waiting for dropdown to appear...")
            await self.page.wait_for_timeout(1500)

            # Try to find and select the best matching dropdown option
            best_match = await self._find_best_dropdown_match(drug_name)

            if best_match:
                logging.info(f"✓ Selected dropdown option: '{best_match}' for drug '{drug_name}'")
            else:
                # Fallback: just press Enter to select first option
                logging.warning(f"No dropdown options found, pressing Enter for: {drug_name}")
                await self.page.keyboard.press('Enter')

            # Wait for the drug to be added
            await self.page.wait_for_timeout(1000)

            logging.debug(f"Successfully added drug: {drug_name}")

        except Exception as e:
            logging.warning(f"Error adding drug {drug_name}: {str(e)}")
            raise

    async def _find_best_dropdown_match(self, drug_name):
        """
        Find and select the best matching option from the dropdown

        Args:
            drug_name: The drug name to match

        Returns:
            str: The selected option text, or None if no options found
        """
        try:
            # Common dropdown selectors for vue-select
            dropdown_selectors = [
                "#vs1__listbox li",  # vue-select dropdown items
                ".vs__dropdown-menu li",
                "[role='option']",
                ".vs__dropdown-option"
            ]

            dropdown_options = []
            selected_selector = None

            # Try each selector to find dropdown options
            for selector in dropdown_selectors:
                elements = await self.page.query_selector_all(selector)
                if elements:
                    selected_selector = selector
                    logging.debug(f"Found {len(elements)} dropdown options using selector: {selector}")

                    # Get text from each option
                    for element in elements:
                        try:
                            text = await element.inner_text()
                            if text and text.strip():
                                dropdown_options.append({
                                    'text': text.strip(),
                                    'element': element
                                })
                        except:
                            continue

                    if dropdown_options:
                        break

            if not dropdown_options:
                logging.warning("No dropdown options found")
                return None

            # Log all available options
            logging.info(f"Available dropdown options for '{drug_name}':")
            for i, option in enumerate(dropdown_options):
                logging.info(f"  {i+1}. {option['text']}")

            # Find best match
            best_match = self._select_best_match(drug_name, dropdown_options)

            if best_match:
                # Click on the best match
                await best_match['element'].click()
                await self.page.wait_for_timeout(500)
                return best_match['text']

            return None

        except Exception as e:
            logging.error(f"Error finding dropdown match: {str(e)}")
            return None

    def _select_best_match(self, drug_name, options):
        """
        Select the best matching option using fuzzy matching

        Args:
            drug_name: The drug name to match
            options: List of option dictionaries with 'text' and 'element' keys

        Returns:
            dict: Best matching option, or None
        """
        if not options:
            return None

        drug_name_lower = drug_name.lower().strip()

        # Strategy 1: Exact match (case-insensitive)
        for option in options:
            option_text_lower = option['text'].lower().strip()
            if drug_name_lower == option_text_lower:
                logging.info(f"✓ EXACT MATCH: '{option['text']}'")
                return option

        # Strategy 2: Starts with match
        for option in options:
            option_text_lower = option['text'].lower().strip()
            if option_text_lower.startswith(drug_name_lower):
                logging.info(f"✓ STARTS WITH MATCH: '{option['text']}'")
                return option

        # Strategy 3: Contains match
        for option in options:
            option_text_lower = option['text'].lower().strip()
            if drug_name_lower in option_text_lower:
                logging.info(f"✓ CONTAINS MATCH: '{option['text']}'")
                return option

        # Strategy 4: Reverse contains (drug name contains option)
        for option in options:
            option_text_lower = option['text'].lower().strip()
            # Extract just the drug name part (before any parentheses or brackets)
            option_drug_name = option_text_lower.split('(')[0].split('[')[0].strip()
            if option_drug_name in drug_name_lower:
                logging.info(f"✓ REVERSE CONTAINS MATCH: '{option['text']}'")
                return option

        # Strategy 5: Levenshtein distance (similarity)
        best_option = None
        best_similarity = 0

        for option in options:
            option_text_lower = option['text'].lower().strip()
            # Extract just the drug name part
            option_drug_name = option_text_lower.split('(')[0].split('[')[0].strip()

            # Calculate simple similarity score
            similarity = self._calculate_similarity(drug_name_lower, option_drug_name)

            if similarity > best_similarity:
                best_similarity = similarity
                best_option = option

        if best_option and best_similarity > 0.5:  # At least 50% similar
            logging.info(f"✓ SIMILARITY MATCH ({best_similarity:.2%}): '{best_option['text']}'")
            return best_option

        # If all strategies fail, return first option as last resort
        logging.warning(f"⚠ NO GOOD MATCH FOUND - Using first option: '{options[0]['text']}'")
        return options[0]

    def _calculate_similarity(self, str1, str2):
        """
        Calculate simple similarity score between two strings

        Args:
            str1: First string
            str2: Second string

        Returns:
            float: Similarity score between 0 and 1
        """
        # Simple character-based similarity
        if not str1 or not str2:
            return 0.0

        # Count matching characters in order
        matches = 0
        i = j = 0

        while i < len(str1) and j < len(str2):
            if str1[i] == str2[j]:
                matches += 1
                i += 1
                j += 1
            else:
                j += 1

        # Normalize by average length
        avg_len = (len(str1) + len(str2)) / 2
        return matches / avg_len if avg_len > 0 else 0.0

    async def _click_check_button(self):
        """Click the 'Check Interactions' button with multiple fallback strategies"""
        # Strategy 1: Try the specific selector provided by user
        try:
            logging.debug(f"Trying primary selector: {self.check_button_selector}")
            await self.page.wait_for_selector(self.check_button_selector, state='visible', timeout=10000)
            await self.page.click(self.check_button_selector)
            logging.debug("Successfully clicked button with primary selector")
            return
        except Exception as e:
            logging.debug(f"Primary selector failed: {e}")

        # Strategy 2: Try alternative selectors
        alternative_selectors = [
            "a.button.dark.check-interactions",
            "a.check-interactions",
            "a:has-text('Check Interactions')",
            "xpath=//a[contains(@class, 'check-interactions')]",
            "xpath=//a[contains(text(), 'Check Interactions')]"
        ]

        for selector in alternative_selectors:
            try:
                logging.debug(f"Trying alternative selector: {selector}")
                await self.page.wait_for_selector(selector, state='visible', timeout=5000)
                await self.page.click(selector)
                logging.debug(f"Successfully clicked button with selector: {selector}")
                return
            except Exception as e:
                logging.debug(f"Selector {selector} failed: {e}")
                continue

        # If all strategies failed, raise exception
        raise Exception("Could not find Check Interactions button with any known selector")

    async def _extract_severity_and_text(self, drug1, drug2):
        """
        Extract DDI severity and text from the results page
        Uses multiple fallback strategies for robust extraction

        Returns:
            tuple: (severity, text) where severity is str (Major, Moderate, Minor, None, or Error)
        """
        try:
            logging.info("="*60)
            logging.info("EXTRACTING INTERACTION DATA")
            logging.info("="*60)

            # STEP 1: Check if result container exists
            logging.debug("Step 1: Looking for result container...")
            result_container = self.page.locator(self.result_container_selector)
            container_count = await result_container.count()

            if container_count == 0:
                logging.info("✗ RESULT CONTAINER NOT FOUND")
                logging.info("→ Assumption: NO interaction found")
                await self._save_debug_info(f"no_interaction_{drug1}_{drug2}")
                raise Exception(f"No interaction found for {drug1} + {drug2}")

            logging.info(f"✓ RESULT CONTAINER FOUND ({container_count} elements)")

            # Save debug info for inspection
            await self._save_debug_info(f"interaction_{drug1}_{drug2}")

            # STEP 2: Extract severity with multiple strategies
            logging.debug("Step 2: Extracting severity...")
            severity = await self._extract_severity()

            # STEP 3: Extract description text
            logging.debug("Step 3: Extracting description text...")
            description_text = await self._extract_description()

            logging.info(f"✓ EXTRACTION COMPLETE: Severity={severity}, Text length={len(description_text)}")

            return (severity, description_text)

        except Exception as e:
            logging.error(f"Error in _extract_severity_and_text: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            await self._save_debug_info(f"extraction_error_{drug1}_{drug2}")
            raise

    async def _extract_severity(self):
        """
        Extract severity using multiple fallback strategies

        Returns:
            str: Severity (Major, Moderate, Minor, or None)
        """
        # Strategy 1: Use the specific severity selector
        try:
            logging.debug("Strategy 1: Using specific severity selector")
            logging.debug(f"Severity selector: {self.severity_selector}")
            severity_element = self.page.locator(self.severity_selector)
            severity_text = await severity_element.inner_text(timeout=5000)
            severity_text = severity_text.strip()

            logging.info(f"Strategy 1 - Extracted text: '{severity_text}'")

            # Check if severity contains valid keywords (case-insensitive)
            severity_text_upper = severity_text.upper()
            if "MAJOR" in severity_text_upper:
                logging.info("✓ SEVERITY EXTRACTED: Major (Strategy 1)")
                return "Major"
            elif "MODERATE" in severity_text_upper:
                logging.info("✓ SEVERITY EXTRACTED: Moderate (Strategy 1)")
                return "Moderate"
            elif "MINOR" in severity_text_upper:
                logging.info("✓ SEVERITY EXTRACTED: Minor (Strategy 1)")
                return "Minor"
            else:
                logging.warning(f"Severity text found but no valid keyword: '{severity_text}'")
        except Exception as e:
            logging.debug(f"Strategy 1 failed: {e}")

        # Strategy 2: Look for any element with severity class
        try:
            logging.debug("Strategy 2: Looking for elements with 'severity' in class")
            severity_elements = await self.page.query_selector_all("[class*='severity']")
            for element in severity_elements:
                element_text = await element.inner_text()
                element_text = element_text.strip().upper()

                if "MAJOR" in element_text:
                    logging.info("✓ SEVERITY EXTRACTED: Major (Strategy 2)")
                    return "Major"
                elif "MODERATE" in element_text:
                    logging.info("✓ SEVERITY EXTRACTED: Moderate (Strategy 2)")
                    return "Moderate"
                elif "MINOR" in element_text:
                    logging.info("✓ SEVERITY EXTRACTED: Minor (Strategy 2)")
                    return "Minor"
        except Exception as e:
            logging.debug(f"Strategy 2 failed: {e}")

        # Strategy 3: Search entire page content
        try:
            logging.debug("Strategy 3: Searching page content")
            page_content = await self.page.content()
            content_upper = page_content.upper()

            # Look for severity keywords in specific context
            if "MAJOR" in content_upper:
                logging.info("✓ SEVERITY EXTRACTED: Major (Strategy 3 - page content)")
                return "Major"
            elif "MODERATE" in content_upper:
                logging.info("✓ SEVERITY EXTRACTED: Moderate (Strategy 3 - page content)")
                return "Moderate"
            elif "MINOR" in content_upper:
                logging.info("✓ SEVERITY EXTRACTED: Minor (Strategy 3 - page content)")
                return "Minor"
        except Exception as e:
            logging.debug(f"Strategy 3 failed: {e}")

        logging.warning("✗ Could not extract severity with any strategy")
        return "None"

    async def _extract_description(self):
        """
        Extract description text using multiple fallback strategies

        Returns:
            str: Description text
        """
        # Strategy 1: Use the specific description selector
        try:
            logging.debug("Strategy 1: Using specific description selector")
            description_element = self.page.locator(self.description_selector)
            description_text = await description_element.inner_text(timeout=5000)
            description_text = description_text.strip()

            if description_text and len(description_text) > 10:
                logging.info(f"✓ DESCRIPTION EXTRACTED: {len(description_text)} characters (Strategy 1)")
                return description_text
        except Exception as e:
            logging.debug(f"Strategy 1 failed: {e}")

        # Strategy 2: Get text from result container
        try:
            logging.debug("Strategy 2: Getting text from result container")
            container = self.page.locator(self.result_container_selector)
            container_text = await container.inner_text(timeout=5000)
            container_text = container_text.strip()

            if container_text and len(container_text) > 10:
                logging.info(f"✓ DESCRIPTION EXTRACTED: {len(container_text)} characters (Strategy 2)")
                return container_text
        except Exception as e:
            logging.debug(f"Strategy 2 failed: {e}")

        # Strategy 3: Search for any div with substantial text
        try:
            logging.debug("Strategy 3: Looking for divs with substantial text")
            all_divs = await self.page.query_selector_all("div.ddi-widget-body div")
            for div in all_divs:
                div_text = await div.inner_text()
                if len(div_text) > 50:  # Substantial text
                    logging.info(f"✓ DESCRIPTION EXTRACTED: {len(div_text)} characters (Strategy 3)")
                    return div_text.strip()
        except Exception as e:
            logging.debug(f"Strategy 3 failed: {e}")

        logging.warning("✗ Could not extract description with any strategy")
        return "No description found"

    async def _save_debug_info(self, reason="debug"):
        """Save screenshot and HTML for debugging purposes"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Save screenshot
            screenshot_path = f"debug_drugbank_screenshot_{reason}_{timestamp}.png"
            await self.page.screenshot(path=screenshot_path, full_page=True)
            logging.info(f"Debug screenshot saved to {screenshot_path}")

            # Save HTML
            html_path = f"debug_drugbank_page_{reason}_{timestamp}.html"
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


async def process_drug_pairs(input_file, output_file=None, checkpoint_file="ddi_checkpoint_drugbank.csv", start_row=0, end_row=None):
    """
    Process drug pairs from CSV file and check interactions

    Args:
        input_file: Path to CSV file with drug pair columns
        output_file: Path to save results (defaults to input_file)
        checkpoint_file: Path to checkpoint file for saving progress
        start_row: Starting row index (0-based)
        end_row: Ending row index (exclusive), None for all rows
    """
    # Read the input file
    logging.info(f"Reading drug pairs from: {input_file}")

    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        logging.error(f"Error reading file: {e}")
        return

    # Validate columns
    if 'Drug_A_Name' not in df.columns or 'Drug_B_Name' not in df.columns:
        logging.error("File must contain 'Drug_A_Name' and 'Drug_B_Name' columns")
        logging.info(f"Found columns: {df.columns.tolist()}")
        return

    drug1_col = 'Drug_A_Name'
    drug2_col = 'Drug_B_Name'
    severity_col = 'DrugBank_Severity'
    text_col = 'DrugBank_Text'

    # Add columns if they don't exist
    if severity_col not in df.columns:
        df[severity_col] = pd.Series(dtype='object')
        logging.info(f"Added {severity_col} column")

    if text_col not in df.columns:
        df[text_col] = pd.Series(dtype='object')
        logging.info(f"Added {text_col} column")

    # Set output file
    if output_file is None:
        output_file = input_file

    # Determine range
    if end_row is None:
        end_row = len(df)

    # Load checkpoint if it exists
    if start_row == 0 and Path(checkpoint_file).exists():
        try:
            checkpoint_df = pd.read_csv(checkpoint_file)
            completed_rows = checkpoint_df[checkpoint_df['Status'] == 'Success']
            if not completed_rows.empty:
                start_row = len(completed_rows)
                logging.info(f"Resuming from checkpoint. Already processed {start_row} drug pairs")

                # Update df with checkpoint data
                for idx, row in checkpoint_df.iterrows():
                    if idx < len(df):
                        if 'DrugBank_Severity' in checkpoint_df.columns:
                            df.at[idx, severity_col] = row['DrugBank_Severity']
                        if 'DrugBank_Text' in checkpoint_df.columns:
                            df.at[idx, text_col] = row['DrugBank_Text']
        except Exception as e:
            logging.warning(f"Could not load checkpoint: {e}")

    # Initialize scraper
    scraper = DrugBankDDIScraper(headless=False, delay_between_requests=2.5)
    await scraper.initialize()

    try:
        total_pairs = end_row - start_row
        logging.info(f"Processing {total_pairs} drug pairs (rows {start_row} to {end_row - 1})")

        # Process each drug pair
        for idx in range(start_row, end_row):
            row = df.iloc[idx]
            drug1 = str(row[drug1_col]).strip()
            drug2 = str(row[drug2_col]).strip()

            # Skip if already processed
            current_severity = df.at[idx, severity_col]
            if pd.notna(current_severity) and current_severity not in ['Error', 'Timeout', 'TBD', '']:
                logging.info(f"[{idx+1}/{len(df)}] Skipping {drug1} + {drug2} (already processed)")
                continue

            logging.info(f"\n{'='*60}")
            logging.info(f"Progress: {idx+1}/{len(df)} ({(idx+1)/len(df)*100:.1f}%)")
            logging.info(f"{'='*60}")

            # Check interaction
            result = await scraper.check_interaction(drug1, drug2)

            # Update dataframe
            df.at[idx, severity_col] = result['DrugBank_Severity']
            df.at[idx, text_col] = result['DrugBank_Text']

            # Save progress every 10 rows
            if (idx + 1) % 10 == 0 or idx == end_row - 1:
                df.to_csv(output_file, index=False)
                logging.info(f"Progress saved to {output_file} (row {idx + 1}/{len(df)})")

            # Save checkpoint
            checkpoint_data = df[[drug1_col, drug2_col, severity_col, text_col]].copy()
            checkpoint_data.columns = ['Drug1', 'Drug2', 'DrugBank_Severity', 'DrugBank_Text']
            checkpoint_data['Status'] = checkpoint_data['DrugBank_Severity'].apply(
                lambda x: 'Success' if x not in ['Error', 'Timeout', None, 'TBD', ''] else 'Failed'
            )
            checkpoint_data['Check_Timestamp'] = result['Check_Timestamp']
            checkpoint_data.to_csv(checkpoint_file, index=False)

            # Rate limiting
            if idx < end_row - 1:
                random_delay_ms = random.randint(1000, 2000)
                logging.info(f"Waiting {random_delay_ms/1000:.1f} seconds before next request...")
                await scraper.page.wait_for_timeout(random_delay_ms)

        # Final save
        df.to_csv(output_file, index=False)

        # Print summary
        logging.info(f"\n{'='*60}")
        logging.info("SCRAPING COMPLETE!")
        logging.info(f"{'='*60}")
        logging.info(f"Total drug pairs processed: {total_pairs}")

        severity_counts = df[severity_col].value_counts()
        logging.info("\nSeverity Distribution:")
        for severity, count in severity_counts.items():
            logging.info(f"  {severity}: {count}")

        logging.info(f"\nResults saved to: {output_file}")
        logging.info(f"{'='*60}")

    except KeyboardInterrupt:
        logging.warning("\nScraping interrupted by user")
        df.to_csv(output_file, index=False)
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

    parser = argparse.ArgumentParser(description='Check drug-drug interactions on DrugBank using Playwright')
    parser.add_argument('input_file', help='CSV file with Drug_A_Name and Drug_B_Name columns')
    parser.add_argument('--output', '-o', help='Output file (defaults to input file)')
    parser.add_argument('--checkpoint', '-c', default='ddi_checkpoint_drugbank.csv',
                       help='Checkpoint file for progress tracking')
    parser.add_argument('--start', '-s', type=int, default=0,
                       help='Starting row index (0-based)')
    parser.add_argument('--end', '-e', type=int, default=None,
                       help='Ending row index (exclusive)')
    parser.add_argument('--delay', '-d', type=float, default=2.5,
                       help='Delay between requests in seconds (minimum 2.0)')

    args = parser.parse_args()

    # Validate input file exists
    if not Path(args.input_file).exists():
        logging.error(f"Input file not found: {args.input_file}")
        return

    await process_drug_pairs(args.input_file, args.output, args.checkpoint, args.start, args.end)


if __name__ == "__main__":
    asyncio.run(main())
