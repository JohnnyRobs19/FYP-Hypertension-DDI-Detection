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
            'DrugsCom_Severity': 'Error',
            'DrugsCom_Text': 'Error extracting interaction information',
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
                await self.page.wait_for_timeout(2000)  # Human-like delay
            except Exception as e:
                logging.warning(f"Could not load homepage, trying direct navigation: {e}")

            # Navigate to the drug interaction checker
            url = "https://www.drugs.com/drug_interactions.html"
            logging.debug(f"Navigating to {url}")
            # Use 'load' instead of 'networkidle' to avoid waiting for all network activity
            await self.page.goto(url, wait_until='load', timeout=30000)

            # Wait a bit for page to fully load (human-like behavior)
            await self.page.wait_for_timeout(2000)

            # Add first drug
            logging.debug(f"Adding first drug: {drug1}")
            await self._add_drug(drug1)

            # Random delay between adding drugs (human-like)
            await self.page.wait_for_timeout(random.randint(1500, 2500))

            # Add second drug
            logging.debug(f"Adding second drug: {drug2}")
            await self._add_drug(drug2)

            # Verify that both drugs were added to the list
            await self.page.wait_for_timeout(random.randint(500, 1000))
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
            delay = random.randint(1000, 2000)
            logging.debug(f"Waiting {delay/1000:.1f} seconds before looking for Check Interactions button...")
            await self.page.wait_for_timeout(delay)

            # Click the "Check Interactions" button
            logging.info("Searching for 'Check Interactions' button...")

            # Use the specific selector for the Check Interactions button
            check_button_selector = "#interaction_list > div > a"

            try:
                logging.debug(f"Trying selector: {check_button_selector}")
                await self.page.wait_for_selector(check_button_selector, state='visible', timeout=15000)
                await self.page.click(check_button_selector)
                logging.debug(f"Successfully clicked button with selector: {check_button_selector}")
            except Exception as e:
                logging.error(f"Could not find or click button with selector {check_button_selector}: {str(e)}")

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

                raise Exception(f"Could not find or click the 'Check Interactions' button with selector: {check_button_selector}")

            # Wait for results page to load
            await self.page.wait_for_timeout(2000)  # 2 seconds
            await self.page.wait_for_load_state('load', timeout=30000)

            # Wait for dynamic content to render
            # Give the page time to display either:
            # - "Interactions between your drugs" section (if drug-drug interactions exist)
            # - "Food Interactions" or "Disease Interactions" only (if no drug-drug interactions)
            logging.info("Waiting for interaction results to render...")
            await self.page.wait_for_timeout(3000)  # 3 seconds for dynamic content

            # Extract the DDI severity and text using Header Guard logic
            # This will return ("None", "...") if no "Interactions between your drugs" header is found
            severity, interaction_text = await self._extract_severity()

            result['DrugsCom_Severity'] = severity
            result['DrugsCom_Text'] = interaction_text

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
                logging.info(f"Result: {drug1} + {drug2} = {severity} (no drug-drug interactions found)")
            else:
                logging.info(f"Result: {drug1} + {drug2} = {severity}")
                logging.debug(f"Interaction text: {interaction_text[:100]}...")

        except PlaywrightTimeoutError as e:
            error_msg = f"Timeout error: {str(e)}"
            logging.error(f"Timeout checking {drug1} + {drug2}: {error_msg}")
            result['Error_Message'] = error_msg
            result['DrugsCom_Severity'] = 'Timeout'
            result['DrugsCom_Text'] = 'Request timed out'

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            logging.error(f"Error checking {drug1} + {drug2}: {error_msg}")
            result['Error_Message'] = error_msg
            result['DrugsCom_Severity'] = 'Error'
            result['DrugsCom_Text'] = f'Error: {str(e)}'

        return result

    async def _add_drug(self, drug_name):
        """
        Add a drug to the interaction checker

        Args:
            drug_name: Name of the drug to add
        """
        try:
            # The input field ID changes after adding the first drug:
            # - Initial state: #livesearch-interaction-basic
            # - After first drug: #livesearch-interaction
            # Try both selectors
            search_input_selectors = [
                "#livesearch-interaction-basic",
                "#livesearch-interaction"
            ]

            search_input_selector = None
            for selector in search_input_selectors:
                try:
                    await self.page.wait_for_selector(selector, state='visible', timeout=3000)
                    search_input_selector = selector
                    logging.debug(f"Found search input with selector: {selector}")
                    break
                except Exception:
                    continue

            if not search_input_selector:
                raise Exception("Could not find search input field with any known selector")

            # Clear any existing text in the input field
            await self.page.fill(search_input_selector, "")
            await self.page.wait_for_timeout(500)  # Brief pause to ensure field is ready

            # Type the drug name character by character (more human-like)
            await self.page.type(search_input_selector, drug_name, delay=random.randint(50, 150))

            # Wait briefly for the field to register the input
            await self.page.wait_for_timeout(500)

            # Press Enter to add the drug
            logging.debug(f"Pressing Enter to add drug: {drug_name}")
            await self.page.keyboard.press('Enter')

            # Wait for the drug to be added and input field to reset
            await self.page.wait_for_timeout(1500)

            # Clear the input field after adding the drug
            # This ensures a clean state for the next drug
            try:
                # After pressing Enter, the input field should be #livesearch-interaction
                clear_selector = "#livesearch-interaction"
                await self.page.wait_for_selector(clear_selector, state='visible', timeout=2000)
                await self.page.fill(clear_selector, "")
                logging.debug("Cleared input field after adding drug")
            except Exception as e:
                logging.debug(f"Could not clear input field (may already be cleared): {e}")

        except Exception as e:
            logging.warning(f"Error adding drug {drug_name}: {str(e)}")
            raise

    async def _extract_severity(self):
        """
        Extract DDI severity and text from the results page using strict Header Guard logic:
        1. Search for the SPECIFIC heading: "Interactions between your drugs"
        2. If found: Extract severity AND text ONLY from the content immediately after that header
        3. If NOT found: Return "None" (no drug-drug interactions)

        This strictly targets Drug-Drug Interactions and ignores Food/Disease interactions.

        Returns:
            tuple: (severity, text) where severity is str (Major, Moderate, Minor, None, or Error)
                   and text is str (interaction description or appropriate message)
        """
        try:
            logging.info("="*60)
            logging.info("HEADER GUARD LOGIC: Searching for drug-drug interaction header")
            logging.info("="*60)

            # STEP 1: THE HEADER GUARD - Look for the specific heading
            # Use Playwright's get_by_role to find the exact heading
            try:
                # Try to find the heading "Interactions between your drugs"
                logging.debug("Searching for heading: 'Interactions between your drugs'")

                # Method 1: Use get_by_role (most reliable)
                try:
                    header = self.page.get_by_role("heading", name="Interactions between your drugs")
                    header_visible = await header.is_visible(timeout=5000)

                    if header_visible:
                        logging.info("✓ HEADER FOUND: 'Interactions between your drugs' heading is visible")
                    else:
                        logging.info("✗ HEADER NOT FOUND: Heading exists but not visible")
                        return "None"

                except Exception as e:
                    logging.debug(f"get_by_role method failed: {e}")
                    # Fallback: Try with CSS/XPath selectors
                    header = None

                    # Try multiple heading tag types (h2, h3)
                    heading_selectors = [
                        'h2:has-text("Interactions between your drugs")',
                        'h3:has-text("Interactions between your drugs")',
                        'xpath=//h2[contains(text(), "Interactions between your drugs")]',
                        'xpath=//h3[contains(text(), "Interactions between your drugs")]'
                    ]

                    for selector in heading_selectors:
                        try:
                            logging.debug(f"Trying selector: {selector}")
                            header_element = await self.page.query_selector(selector)
                            if header_element:
                                is_visible = await header_element.is_visible()
                                if is_visible:
                                    logging.info(f"✓ HEADER FOUND with selector: {selector}")
                                    header = header_element
                                    break
                        except Exception as sel_error:
                            logging.debug(f"Selector {selector} failed: {sel_error}")
                            continue

                    if not header:
                        logging.info("✗ HEADER NOT FOUND: No 'Interactions between your drugs' heading found")
                        logging.info("→ Assumption: NO drug-drug interactions present (may be Food/Disease only)")
                        return ("None", "No drug-drug interactions found")

            except Exception as e:
                logging.warning(f"Error searching for header: {e}")
                logging.info("✗ HEADER NOT FOUND: Error during search")
                return ("None", "No drug-drug interactions found")

            # STEP 2: HEADER FOUND - Extract content from the section immediately after
            logging.info("STEP 2: Header found, extracting severity from drug-drug interaction section")

            # Find the wrapper div immediately after the heading
            interaction_section = None

            try:
                # Use XPath to find the div immediately following the h2/h3 heading
                xpath_selector = 'xpath=//h2[contains(text(), "Interactions between your drugs")]/following-sibling::div[1]'
                interaction_section = await self.page.query_selector(xpath_selector)

                if not interaction_section:
                    # Try with h3 if h2 didn't work
                    xpath_selector = 'xpath=//h3[contains(text(), "Interactions between your drugs")]/following-sibling::div[1]'
                    interaction_section = await self.page.query_selector(xpath_selector)

                if interaction_section:
                    section_class = await interaction_section.get_attribute('class') or ''
                    logging.debug(f"Found interaction section (class: {section_class})")
                else:
                    logging.warning("Could not find the div immediately after the header")
                    await self._save_debug_info("header_found_but_no_section")
                    return ("None", "No drug-drug interactions found")

            except Exception as e:
                logging.warning(f"Error finding interaction section: {e}")
                await self._save_debug_info("section_extraction_error")
                return ("None", "No drug-drug interactions found")

            # STEP 3: Extract the full section text for DrugsCom_Text column
            section_text = ""
            try:
                section_text = await interaction_section.inner_text()
                logging.debug(f"Section text preview: {section_text[:150]}...")

                # Check for "No drug ⬌ drug interactions were found" message
                if "No drug" in section_text and "drug interactions were found" in section_text:
                    logging.info("✓ Found 'No drug-drug interactions were found' message in section")
                    return ("None", "No drug-drug interactions found")

            except Exception as e:
                logging.debug(f"Error reading section text: {e}")
                section_text = ""

            # STEP 4: Extract severity label from this section ONLY
            logging.debug("Searching for severity label within drug-drug interaction section...")

            # Look for severity label within the interaction section
            severity_selectors = [
                "span.ddc-status-label",  # Primary selector
                "span[class*='status-category']",  # Severity spans with status-category in class
                "div > span",  # Generic spans
            ]

            for selector in severity_selectors:
                try:
                    severity_elements = await interaction_section.query_selector_all(selector)
                    logging.debug(f"Found {len(severity_elements)} elements with selector: {selector}")

                    for element in severity_elements:
                        try:
                            element_class = await element.get_attribute("class") or ""
                            element_text = await element.inner_text()
                            element_text_clean = element_text.strip().upper()

                            logging.debug(f"  Checking element - class: {element_class}, text: {element_text_clean}")

                            # Method 1: Check class for severity category
                            if "status-category-major" in element_class:
                                logging.info("✓ SEVERITY EXTRACTED: Major (from class)")
                                return ("Major", section_text.strip())
                            elif "status-category-moderate" in element_class:
                                logging.info("✓ SEVERITY EXTRACTED: Moderate (from class)")
                                return ("Moderate", section_text.strip())
                            elif "status-category-minor" in element_class:
                                logging.info("✓ SEVERITY EXTRACTED: Minor (from class)")
                                return ("Minor", section_text.strip())

                            # Method 2: Check text content
                            if element_text_clean in ["MAJOR", "MODERATE", "MINOR"]:
                                severity_found = element_text_clean.capitalize()
                                logging.info(f"✓ SEVERITY EXTRACTED: {severity_found} (from text)")
                                return (severity_found, section_text.strip())

                            # Method 3: Check if text contains severity keyword
                            for severity_keyword in ["MAJOR", "MODERATE", "MINOR"]:
                                if severity_keyword in element_text_clean:
                                    logging.info(f"✓ SEVERITY EXTRACTED: {severity_keyword.capitalize()} (text contains keyword)")
                                    return (severity_keyword.capitalize(), section_text.strip())

                        except Exception as elem_error:
                            logging.debug(f"  Error processing element: {elem_error}")
                            continue

                except Exception as selector_error:
                    logging.debug(f"Error with selector {selector}: {selector_error}")
                    continue

            # STEP 5: Fallback - check HTML content of section for severity class names
            logging.debug("Fallback: Checking HTML content for severity class names...")
            try:
                section_html = await interaction_section.inner_html()
                content_lower = section_html.lower()

                # Check for severity classes in HTML
                if 'status-category-major' in content_lower:
                    logging.info("✓ SEVERITY EXTRACTED: Major (from HTML class)")
                    return ("Major", section_text.strip())
                elif 'status-category-moderate' in content_lower:
                    logging.info("✓ SEVERITY EXTRACTED: Moderate (from HTML class)")
                    return ("Moderate", section_text.strip())
                elif 'status-category-minor' in content_lower:
                    logging.info("✓ SEVERITY EXTRACTED: Minor (from HTML class)")
                    return ("Minor", section_text.strip())

            except Exception as e:
                logging.debug(f"Error checking HTML content: {e}")

            # STEP 6: No severity found in the drug-drug interaction section
            logging.warning("✗ Could not extract severity from drug-drug interaction section")
            logging.info("→ Header was found but no severity label detected")
            await self._save_debug_info("header_found_no_severity")
            return ("None", section_text.strip() if section_text else "No drug-drug interactions found")

        except Exception as e:
            logging.error(f"Error in _extract_severity: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            await self._save_debug_info("extraction_error")
            return ("Error", "Error extracting interaction information")

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
    Process drug pairs from CSV/Excel file and check interactions

    Args:
        input_file: Path to CSV or Excel file with drug pair columns
        output_file: Path to save results (defaults to input_file)
        checkpoint_file: Path to checkpoint file for saving progress
    """
    # Read the input file (CSV or Excel)
    logging.info(f"Reading drug pairs from: {input_file}")

    try:
        # Detect file type and read accordingly
        if input_file.endswith('.csv'):
            df = pd.read_csv(input_file)
        elif input_file.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(input_file)
        else:
            logging.error("Unsupported file format. Please use .csv, .xlsx, or .xls")
            return
    except Exception as e:
        logging.error(f"Error reading file: {e}")
        return

    # Validate columns - support both naming conventions
    # CSV template uses: Drug_A_Name, Drug_B_Name, DrugsCom_Severity, DrugsCom_Text
    # Legacy Excel uses: Drug1, Drug2, DDI_Severity

    if 'Drug_A_Name' in df.columns and 'Drug_B_Name' in df.columns:
        # CSV template format
        drug1_col = 'Drug_A_Name'
        drug2_col = 'Drug_B_Name'
        severity_col = 'DrugsCom_Severity'
        text_col = 'DrugsCom_Text'
        logging.info("Using CSV template format (Drug_A_Name, Drug_B_Name, DrugsCom_Severity, DrugsCom_Text)")
    elif 'Drug1' in df.columns and 'Drug2' in df.columns:
        # Legacy Excel format
        drug1_col = 'Drug1'
        drug2_col = 'Drug2'
        severity_col = 'DrugsCom_Severity'
        text_col = 'DrugsCom_Text'
        logging.info("Using legacy Excel format (Drug1, Drug2)")
    else:
        logging.error("File must contain either 'Drug_A_Name' and 'Drug_B_Name' OR 'Drug1' and 'Drug2' columns")
        logging.info(f"Found columns: {df.columns.tolist()}")
        return

    # Add DrugsCom_Severity and DrugsCom_Text columns if they don't exist
    if severity_col not in df.columns:
        df[severity_col] = pd.Series(dtype='object')
        logging.info(f"Added {severity_col} column")
    else:
        df[severity_col] = df[severity_col].astype('object')

    if text_col not in df.columns:
        df[text_col] = pd.Series(dtype='object')
        logging.info(f"Added {text_col} column")
    else:
        df[text_col] = df[text_col].astype('object')

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
                        if 'DrugsCom_Severity' in checkpoint_df.columns:
                            df.at[idx, severity_col] = row['DrugsCom_Severity']
                        if 'DrugsCom_Text' in checkpoint_df.columns:
                            df.at[idx, text_col] = row['DrugsCom_Text']
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
            drug1 = str(row[drug1_col]).strip()
            drug2 = str(row[drug2_col]).strip()

            # Skip if already processed (check if severity is not TBD, Error, or Timeout)
            current_severity = df.at[idx, severity_col]
            if pd.notna(current_severity) and current_severity not in ['Error', 'Timeout', 'TBD', '']:
                logging.info(f"[{idx+1}/{total_pairs}] Skipping {drug1} + {drug2} (already processed)")
                continue

            logging.info(f"\n{'='*60}")
            logging.info(f"Progress: {idx+1}/{total_pairs} ({(idx+1)/total_pairs*100:.1f}%)")
            logging.info(f"{'='*60}")

            # Check interaction
            result = await scraper.check_interaction(drug1, drug2)

            # Update dataframe with both severity and text
            df.at[idx, severity_col] = result['DrugsCom_Severity']
            df.at[idx, text_col] = result['DrugsCom_Text']

            # Save progress every 10 rows (or on the last row)
            if (idx + 1) % 10 == 0 or idx == total_pairs - 1:
                if input_file.endswith('.csv'):
                    df.to_csv(output_file, index=False)
                else:
                    df.to_excel(output_file, index=False)
                logging.info(f"Progress saved to {output_file} (row {idx + 1}/{total_pairs})")

            # Save checkpoint after each row (lightweight CSV operation)
            checkpoint_data = df[[drug1_col, drug2_col, severity_col, text_col]].copy()
            checkpoint_data.columns = ['Drug1', 'Drug2', 'DrugsCom_Severity', 'DrugsCom_Text']  # Normalize for checkpoint
            checkpoint_data['Status'] = checkpoint_data['DrugsCom_Severity'].apply(
                lambda x: 'Success' if x not in ['Error', 'Timeout', None] else 'Failed'
            )
            checkpoint_data['Check_Timestamp'] = result['Check_Timestamp']
            checkpoint_data.to_csv(checkpoint_file, index=False)

            # Rate limiting - wait between requests to appear more human
            if idx < total_pairs - 1:  # Don't wait after the last pair
                # Use page.wait_for_timeout for rate limiting (1000ms = 1 second minimum)
                random_delay_ms = random.randint(1000, 2000)  # Random 1-2 seconds
                logging.info(f"Waiting {random_delay_ms/1000:.1f} seconds before next request...")
                await scraper.page.wait_for_timeout(random_delay_ms)

                # Additional delay based on configured delay_between_requests
                if scraper.delay_between_requests > 2.0:
                    additional_delay = int((scraper.delay_between_requests - 2.0) * 1000)
                    await scraper.page.wait_for_timeout(additional_delay)

        # Final save
        if input_file.endswith('.csv'):
            df.to_csv(output_file, index=False)
        else:
            df.to_excel(output_file, index=False)

        # Print summary
        logging.info(f"\n{'='*60}")
        logging.info("SCRAPING COMPLETE!")
        logging.info(f"{'='*60}")
        logging.info(f"Total drug pairs processed: {total_pairs}")

        # Count severities
        severity_counts = df[severity_col].value_counts()
        logging.info("\nSeverity Distribution:")
        for severity, count in severity_counts.items():
            logging.info(f"  {severity}: {count}")

        logging.info(f"\nResults saved to: {output_file}")
        logging.info(f"{'='*60}")

    except KeyboardInterrupt:
        logging.warning("\nScraping interrupted by user")
        if input_file.endswith('.csv'):
            df.to_csv(output_file, index=False)
        else:
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
    parser.add_argument('input_file', help='CSV or Excel file with drug pair columns (Drug_A_Name/Drug_B_Name or Drug1/Drug2)')
    parser.add_argument('--output', '-o', help='Output file (defaults to input file)')
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
