# DDInter Selenium Scraper - Setup Guide

## Quick Start (3 Steps)

### 1. Install Microsoft Edge WebDriver

✅ **If you already have Microsoft Edge installed on Windows:**
The scraper will automatically use Edge! Just make sure Edge WebDriver is installed:

```bash
# For WSL/Ubuntu - Install Edge WebDriver
sudo apt-get update
sudo apt-get install -y microsoft-edge-stable

# OR manually download EdgeDriver
# Visit: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
```

**Note:** If Edge is installed on your Windows system and you're using WSL, the scraper should work automatically!

### 2. Install Python Dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the Scraper
```bash
python selenium_ddi_scraper.py
```

---

## What It Does

✅ Reads drugs from `DRUGS INTERACTION (HYPERTENSION).xlsx`
✅ Searches each drug on DDInter automatically
✅ Scrolls through all results (handles infinite scroll)
✅ Extracts all drug interactions
✅ Saves to `DRUGS_INTERACTION_COMPLETE.xlsx`
✅ Creates checkpoint every 5 drugs (resumable if interrupted)
✅ Logs everything to `scraping.log`

---

## Running Overnight

The scraper is designed to run unattended:

```bash
# Run in background
nohup python selenium_ddi_scraper.py > output.log 2>&1 &

# Check progress
tail -f scraping.log

# Or monitor in real-time
watch -n 10 'tail -20 scraping.log'
```

---

## Output Files

1. **DRUGS_INTERACTION_COMPLETE.xlsx** - Final results with 3 sheets:
   - `Drug List`: Original drugs
   - `All Interactions`: Complete interaction data
   - `Summary`: Statistics

2. **scraping_checkpoint.csv** - Progress checkpoint (auto-saves every 5 drugs)

3. **scraping.log** - Detailed execution log

---

## Features

### Checkpoint & Resume
- Automatically saves progress every 5 drugs
- If interrupted, just run again - it will resume from checkpoint
- Never loses data

### Error Handling
- Retries on failures
- Logs all errors
- Continues with next drug if one fails

### Performance
- Headless mode (no GUI needed)
- Optimized scrolling
- ~2-5 seconds per drug interaction

---

## Troubleshooting

### Edge/EdgeDriver Issues
```bash
# Check if Edge is accessible
microsoft-edge --version

# Check if msedgedriver is in PATH
which msedgedriver

# If using Windows Edge from WSL, make sure Edge is updated
# Open Edge on Windows and go to edge://settings/help
```

### Permission Errors
```bash
chmod +x selenium_ddi_scraper.py
```

### WSL Display Issues
Scraper runs in headless mode by default, so no display needed!

---

## Estimated Time

- **Small dataset (~50 drugs)**: 5-10 minutes
- **Medium dataset (~200 drugs)**: 30-60 minutes
- **Large dataset (~500 drugs)**: 2-3 hours

---

## Advanced Usage

### Change to Non-Headless (See Browser)
Edit `selenium_ddi_scraper.py` line 49:
```python
scraper = DDInterScraper(headless=False)  # Change True to False
```

### Adjust Scroll Limits
Edit line 84:
```python
def scroll_to_load_all(self, max_scrolls=50):  # Increase if needed
```

---

## Support

Check the log file for errors:
```bash
tail -50 scraping.log
```
