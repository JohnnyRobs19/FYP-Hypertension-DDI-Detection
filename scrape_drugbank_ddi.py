"""
DrugBank DDI Scraper
Scrapes drug-drug interaction data from DrugBank's DDI Checker
"""

import pandas as pd
import asyncio
import random
from playwright.async_api import async_playwright
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('drugbank_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DrugBankScraper:
    def __init__(self, input_csv, output_csv="ddi_checkpoint_drugbank.csv"):
        self.input_csv = input_csv
        self.output_csv = output_csv
        self.df = None
        self.browser = None
        self.page = None

        # Selectors
        self.input_selector = "#vs1__combobox > div.vs__selected-options > input"
        self.check_button_selector = "body > main > div.panel.plugin-panel > div > div.demo-body > div > div.panel-right.col-right.col-xs-12.col-sm-8 > div > div.row.ddi-controls > center > a.button.dark.check-interactions"
        self.result_container_selector = "div > div > div.ddi-widget-body > div > div.form-row.mb-3"
        self.severity_selector = "div > div > div.ddi-widget-body > div > div.form-row.mb-3 > div > div > div.card-row.header-row > div.intx-item.interaction-severity"
        self.description_selector = "div > div > div.ddi-widget-body > div > div.form-row.mb-3 > div > div > div:nth-child(2)"

    def load_csv(self):
        """Load the CSV file"""
        logger.info(f"Loading CSV file: {self.input_csv}")
        self.df = pd.read_csv(self.input_csv)
        logger.info(f"Loaded {len(self.df)} rows")

    def save_checkpoint(self):
        """Save the current dataframe to checkpoint file"""
        self.df.to_csv(self.output_csv, index=False)
        logger.info(f"Checkpoint saved to {self.output_csv}")

    async def setup_browser(self):
        """Initialize Playwright browser"""
        logger.info("Setting up browser...")
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page()
        await self.page.goto("https://dev.drugbank.com/demo/ddi_checker")
        logger.info("Browser ready")

    async def close_browser(self):
        """Close the browser"""
        if self.browser:
            await self.browser.close()
            logger.info("Browser closed")

    async def clear_input_field(self):
        """Clear the input field"""
        await self.page.fill(self.input_selector, "")

    async def input_drug(self, drug_name):
        """Input a drug name and press Enter"""
        logger.info(f"Inputting drug: {drug_name}")

        # Clear the input field
        await self.clear_input_field()

        # Type drug name
        await self.page.type(self.input_selector, drug_name)

        # Wait for dropdown
        await asyncio.sleep(1)

        # Press Enter
        await self.page.keyboard.press("Enter")

        # Small delay after Enter
        await asyncio.sleep(0.5)

    async def check_interactions(self):
        """Click the 'Check Interactions' button"""
        logger.info("Clicking 'Check Interactions' button")
        await self.page.click(self.check_button_selector)

        # Wait for results to load (increase timeout for slower loads)
        await asyncio.sleep(3)

    async def scrape_interaction_data(self, drug_a, drug_b):
        """
        Scrape interaction data for a drug pair
        Returns: (severity, description)
        """
        logger.info(f"Scraping interaction data for {drug_a} + {drug_b}")

        try:
            # Input Drug A
            await self.input_drug(drug_a)

            # Input Drug B
            await self.input_drug(drug_b)

            # Check interactions
            await self.check_interactions()

            # Try to locate the result container
            result_container = self.page.locator(self.result_container_selector)

            # Check if results exist
            count = await result_container.count()

            if count == 0:
                logger.warning(f"No interaction found for {drug_a} + {drug_b}")
                raise Exception(f"No interaction found for {drug_a} + {drug_b}")

            # Extract severity
            severity_element = self.page.locator(self.severity_selector)
            severity_text = await severity_element.inner_text()
            severity_text = severity_text.strip()

            # Check if severity is valid
            severity = None
            if "Major" in severity_text:
                severity = "Major"
            elif "Moderate" in severity_text:
                severity = "Moderate"
            elif "Minor" in severity_text:
                severity = "Minor"
            else:
                logger.warning(f"Unknown severity: {severity_text}")
                severity = severity_text

            # Extract description
            description_element = self.page.locator(self.description_selector)
            description_text = await description_element.inner_text()
            description_text = description_text.strip()

            logger.info(f"Found: Severity={severity}, Description length={len(description_text)}")

            return severity, description_text

        except Exception as e:
            logger.error(f"Error scraping {drug_a} + {drug_b}: {str(e)}")
            raise

    async def process_row(self, index, row):
        """Process a single row"""
        drug_a = row['Drug_A_Name']
        drug_b = row['Drug_B_Name']

        logger.info(f"Processing row {index + 1}: {drug_a} + {drug_b}")

        try:
            severity, description = await self.scrape_interaction_data(drug_a, drug_b)

            # Update dataframe
            self.df.at[index, 'DrugBank_Severity'] = severity
            self.df.at[index, 'DrugBank_Text'] = description

            logger.info(f"Row {index + 1} completed successfully")

        except Exception as e:
            # Handle "No interaction" cases
            self.df.at[index, 'DrugBank_Severity'] = "None"
            self.df.at[index, 'DrugBank_Text'] = f"No interaction found - {str(e)}"
            logger.error(f"Row {index + 1} failed: {str(e)}")

        # Random delay between requests
        delay = random.uniform(1, 2)
        logger.info(f"Waiting {delay:.2f} seconds before next request...")
        await asyncio.sleep(delay)

    async def run(self, start_row=0, end_row=None):
        """
        Run the scraper

        Args:
            start_row: Starting row index (0-based)
            end_row: Ending row index (exclusive), None for all rows
        """
        # Load CSV
        self.load_csv()

        # Setup browser
        await self.setup_browser()

        try:
            # Determine range
            if end_row is None:
                end_row = len(self.df)

            logger.info(f"Processing rows {start_row} to {end_row - 1}")

            # Process each row
            for index in range(start_row, end_row):
                row = self.df.iloc[index]

                # Process the row
                await self.process_row(index, row)

                # Save checkpoint every 10 rows
                if (index + 1) % 10 == 0:
                    self.save_checkpoint()
                    logger.info(f"Checkpoint: Processed {index + 1} rows")

            # Final save
            self.save_checkpoint()
            logger.info("All rows processed!")

        finally:
            # Close browser
            await self.close_browser()


async def main():
    """Main function"""
    input_csv = "FYP_Drug_Interaction_Template.csv"
    output_csv = "ddi_checkpoint_drugbank.csv"

    scraper = DrugBankScraper(input_csv, output_csv)

    # You can specify start and end rows here
    # Example: await scraper.run(start_row=0, end_row=50)  # Process first 50 rows
    await scraper.run()  # Process all rows


if __name__ == "__main__":
    asyncio.run(main())
