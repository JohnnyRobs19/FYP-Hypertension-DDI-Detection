# 🚀 Quick Start - Automated DDI Scraper

## What This Does

✅ Automatically scrapes drug interactions from DDInter website
✅ Reads all **48 drugs** from your Excel file
✅ Uses Microsoft Edge (already installed on your system!)
✅ Saves complete results to Excel with multiple sheets
✅ Runs overnight - no manual work needed

---

## Run in 2 Steps

### Step 1: Install Dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Start Scraping
```bash
bash START_SCRAPER.sh
```

That's it! ☕ Grab a coffee and let it run for 30-60 minutes.

---

## What You'll Get

**Output File:** `DRUGS_INTERACTION_COMPLETE.xlsx`

Contains 3 sheets:
1. **Drug List** - Your original 48 drugs
2. **All Interactions** - Complete DDI data (Drug A, Drug B, Level, Mechanism)
3. **Summary** - Statistics and scraping info

---

## Monitor Progress

```bash
# Watch real-time progress
tail -f scraping.log

# Or check progress every 10 seconds
watch -n 10 'tail -20 scraping.log'
```

---

## Features

### 🔄 Resume Support
- Auto-saves every 5 drugs
- If interrupted, just run again - continues where it left off
- Checkpoint file: `scraping_checkpoint.csv`

### 📊 Your 48 Drugs
The scraper will process:
- ACE Inhibitors (Captopril, Enalapril, Lisinopril, etc.)
- ARBs (Candesartan, Irbesartan, Losartan, etc.)
- Calcium Channel Blockers (Amlodipine, Nifedipine, etc.)
- Diuretics (Hydrochlorothiazide, etc.)
- Beta Blockers (Atenolol, Metoprolol, etc.)
- Alpha Blockers (Doxazosin, Prazosin, etc.)

---

## Run in Background (Overnight)

```bash
# Start in background
nohup bash START_SCRAPER.sh > output.log 2>&1 &

# Check progress
tail -f scraping.log

# Kill if needed
pkill -f selenium_ddi_scraper
```

---

## Using Microsoft Edge

✅ **Already configured!** The scraper uses Edge by default.

If you get Edge driver errors:
1. Make sure Edge is updated (go to `edge://settings/help`)
2. Install Edge WebDriver:
   ```bash
   sudo apt-get update
   sudo apt-get install -y msedgedriver
   ```

---

## Troubleshooting

**Error: "EdgeDriver not found"**
- Make sure Microsoft Edge is installed
- Update Edge to latest version
- Run: `pip install --upgrade selenium`

**Error: "Excel file not found"**
- Make sure you're in the correct directory: `/home/johnnyrobs19/FYP-Hypertension-DDI-Detection`

**Scraper seems stuck**
- It's scrolling through results - this is normal!
- Check `scraping.log` to see current progress

---

## Questions?

Check `SETUP_GUIDE.md` for detailed documentation.
