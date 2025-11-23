# Playwright DDI Scraper - Usage Guide

This guide explains how to use the Playwright-based drug-drug interaction (DDI) scraper for drugs.com.

## Overview

The `playwright_ddi_scraper.py` script automates checking drug-drug interactions on drugs.com using Playwright. It reads drug pairs from an Excel file, checks each pair on the website, and saves the results back to the Excel file.

## Features

- **Automated DDI checking**: Checks drug interactions on drugs.com automatically
- **Excel-based**: Reads from and writes to Excel files
- **Progress saving**: Saves progress after each drug pair
- **Checkpoint support**: Can resume from where it left off if interrupted
- **Rate limiting**: Respectful 3.5-second delay between requests (configurable)
- **Error handling**: Handles timeouts and network issues gracefully
- **Logging**: Detailed logging to file and console

## Installation

### 1. Install Python dependencies

```bash
# Activate virtual environment (if using one)
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install requirements
pip install -r requirements.txt
```

### 2. Install Playwright browsers

After installing the Python packages, you need to install the Playwright browser binaries:

```bash
playwright install chromium
```

Or install all browsers:

```bash
playwright install
```

## Usage

### Step 1: Prepare your Excel file

Your Excel file must have two columns named exactly `Drug1` and `Drug2`:

| Drug1      | Drug2                |
|------------|----------------------|
| Aspirin    | Ibuprofen           |
| Lisinopril | Hydrochlorothiazide |
| Metformin  | Glipizide           |

### Step 2: Run the scraper

Basic usage:

```bash
python playwright_ddi_scraper.py your_drug_pairs.xlsx
```

The scraper will:
1. Read the drug pairs from the Excel file
2. Check each pair on drugs.com
3. Add a `DDI_Severity` column with results
4. Save the file after each drug pair is checked

### Advanced Options

**Specify output file:**
```bash
python playwright_ddi_scraper.py input.xlsx --output results.xlsx
```

**Custom checkpoint file:**
```bash
python playwright_ddi_scraper.py input.xlsx --checkpoint my_checkpoint.csv
```

**Adjust delay between requests:**
```bash
python playwright_ddi_scraper.py input.xlsx --delay 5.0
```
(Minimum 3.0 seconds, higher values are more respectful to the server)

**Full example:**
```bash
python playwright_ddi_scraper.py drug_pairs.xlsx \
    --output ddi_results.xlsx \
    --checkpoint progress.csv \
    --delay 4.0
```

## Creating Sample Drug Pairs

Use the helper script to create a drug pairs Excel file:

### Option 1: Create a simple template
```bash
python create_sample_drug_pairs.py --mode template --output my_pairs.xlsx
```

### Option 2: Generate from a custom drug list
```bash
python create_sample_drug_pairs.py \
    --mode from-list \
    --drugs Aspirin Lisinopril Metformin Amlodipine \
    --output my_pairs.xlsx
```

### Option 3: Generate from hypertension drugs file
```bash
python create_sample_drug_pairs.py \
    --mode from-hypertension \
    --input-file "DRUGS INTERACTION (HYPERTENSION).xlsx" \
    --output hypertension_pairs.xlsx \
    --max-pairs 50
```

This will create all possible unique combinations of the drugs in the hypertension file. Use `--max-pairs` to limit the number (since N drugs create N*(N-1)/2 pairs).

## Output

### Excel File

The script updates your Excel file with a `DDI_Severity` column containing:

- **Minor**: Minor interaction
- **Moderate**: Moderate interaction
- **Major**: Major/severe interaction
- **N/A**: No interaction found
- **Error**: An error occurred during checking
- **Timeout**: Request timed out
- **Unknown**: Severity could not be determined

### Checkpoint File

A CSV file tracking progress with columns:
- `Drug1`, `Drug2`: The drug pair
- `DDI_Severity`: The result
- `Status`: Success or Failed
- `Check_Timestamp`: When it was checked

### Log File

`playwright_ddi_scraper.log` contains detailed logs of the scraping process.

## Resuming Interrupted Sessions

If the scraper is interrupted (Ctrl+C, crash, etc.), simply run the same command again:

```bash
python playwright_ddi_scraper.py drug_pairs.xlsx
```

It will:
1. Load the checkpoint file
2. Skip already-processed pairs
3. Continue from where it left off

## Troubleshooting

### "Excel file must contain 'Drug1' and 'Drug2' columns"

Make sure your Excel file has columns named exactly `Drug1` and `Drug2` (case-sensitive).

### Playwright browser not found

Run:
```bash
playwright install chromium
```

### Rate limiting / Being blocked

Increase the delay between requests:
```bash
python playwright_ddi_scraper.py input.xlsx --delay 5.0
```

### "Could not find severity indicator"

The website structure may have changed. Check the log file for details. The script tries multiple selectors to find the severity.

### Running in headless mode

By default, the browser runs in headless mode (no visible window). To see the browser for debugging, edit the script and change:

```python
scraper = PlaywrightDDIScraper(headless=False)
```

## Best Practices

1. **Start small**: Test with a few drug pairs first
2. **Use checkpoints**: Don't delete checkpoint files until you're done
3. **Monitor logs**: Check the log file if something seems wrong
4. **Be respectful**: Use appropriate delays (3+ seconds)
5. **Backup your data**: Keep a copy of your original Excel file

## Example Workflow

```bash
# 1. Create a sample file with drug pairs
python create_sample_drug_pairs.py \
    --mode from-hypertension \
    --max-pairs 20 \
    --output test_pairs.xlsx

# 2. Run the scraper
python playwright_ddi_scraper.py test_pairs.xlsx

# 3. Check the results
# Open test_pairs.xlsx in Excel/LibreOffice
# Review the DDI_Severity column
```

## Technical Details

### How It Works

1. Opens drugs.com interaction checker
2. Fills in first drug name in the search box
3. Clicks "Add" button
4. Fills in second drug name
5. Clicks "Add" button again
6. Clicks "Check Interactions" button
7. Extracts severity from the results page
8. Saves to Excel and checkpoint files

### Selectors Used

- Search input: `#livesearch-interaction`
- Add button: `#drug-interactions-search > div > button`
- Check button: `#interaction_list > div > a`
- Severity (primary): `#content > div:nth-child(9) > div > div > span`
- Severity (fallback): Multiple alternative selectors

### Rate Limiting

- Minimum 3 seconds between drug pair checks
- Additional delays between adding drugs (1-1.5 seconds)
- Waits for page load events (`networkidle`)

## Support

If you encounter issues:

1. Check the log file: `playwright_ddi_scraper.log`
2. Verify your Excel file format
3. Ensure Playwright browsers are installed
4. Try running with `--delay 5.0` for more stability

## License

This script is for educational and research purposes. Please review drugs.com's terms of service before extensive use.
