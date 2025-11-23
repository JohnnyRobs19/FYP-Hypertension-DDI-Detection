# Hypertension Drug Interaction Data Collection

**Final Year Project - University of Malaya**
**Project:** ML-Driven Detection of Drug Interactions in Hypertensive Patients
**Supervisors:** Dr. Unaizah, Dr. Nurulhuda

---

## 🚀 **NEW: Automated Selenium Scraper (Microsoft Edge)**

**Want to automatically scrape all drug interactions?**

👉 **See `QUICK_START.md` for the 2-step setup!**

The new scraper:
- ✅ Uses Microsoft Edge (already on your system!)
- ✅ Automatically scrapes all 48 drugs from your Excel file
- ✅ Handles infinite scroll and dynamic content
- ✅ Saves to Excel with multiple sheets
- ✅ Runs overnight - complete automation!

```bash
# Quick start:
source venv/bin/activate
pip install -r requirements.txt
bash START_SCRAPER.sh
```

---

## 📋 Project Overview

This project aims to collect drug-drug interaction (DDI) data for hypertension medications to train machine learning models (Random Forest, SVC, Naive Bayes) that can predict interaction severity levels and recommend safer medication pathways aligned with Malaysian Clinical Practice Guidelines.

---

## 📊 Extracted Drug Data

The system successfully extracted **72 unique hypertension drugs** from the provided Excel file, organized into 6 drug classes:

| Drug Class | Count | Examples |
|-----------|-------|----------|
| ACE Inhibitors | 11 | Benazepril, Enalapril, Lisinopril |
| ARBs | 8 | Candesartan, Losartan, Valsartan |
| CCBs (Calcium Channel Blockers) | 12 | Amlodipine, Diltiazem, Nifedipine |
| Diuretics | 20 | Hydrochlorothiazide, Furosemide, Spironolactone |
| Alpha Blockers | 6 | Doxazosin, Prazosin, Terazosin |
| Beta Blockers | 15 | Atenolol, Metoprolol, Propranolol |

**Total pairwise combinations:** 2,556 drug pairs
**Estimated scraping time (at 2s/pair):** ~85 minutes

---

## ⚙️ Setup Instructions

### 1. Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)

### 2. Installation

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Required Files
- `DRUGS INTERACTION (HYPERTENSION).xlsx` - Input Excel file with drug data
- `scrape_drug_interactions.py` - Main scraper script
- `requirements.txt` - Python dependencies

---

## 🚀 Usage

### Dry Run (Extract drugs and show combinations without scraping)
```bash
python scrape_drug_interactions.py dry-run
```

### Test Mode (Test scraping with 3 drug pairs)
```bash
python scrape_drug_interactions.py test
```

### Full Scraping Mode
```bash
python scrape_drug_interactions.py
```

The script will:
1. Extract all drugs from the Excel file
2. Generate 2,556 drug pair combinations
3. Ask for your confirmation before starting
4. Scrape interactions with respectful 2-second delays
5. Auto-save progress every 20 interactions
6. Export results to `drug_interactions_results.csv`

---

## ⚠️ Important Limitations Discovered

### Web Scraping Challenge: JavaScript-Rendered Content

After thorough investigation, we discovered that **Drugs.com requires JavaScript** to load drug interaction data dynamically. This means:

1. **Static HTML scraping cannot access the interaction data** - The interaction checker uses AJAX calls to load results
2. **Simple requests-based scraping will not work** - The page initially loads without interaction data
3. **Alternative approaches are needed** to collect this data

### Tested URLs:
- ❌ `https://www.drugs.com/interactions-check.php?drug_list=drug1,drug2` - Requires JavaScript
- ❌ `https://www.drugs.com/drug-interactions/drug1,drug2.html` - Shows individual drug info, not pairwise interactions

---

## 🔄 Alternative Approaches

### Option 1: Browser Automation with Selenium (Recommended)

Use Selenium with a headless browser to interact with the JavaScript-based interface.

**Pros:**
- Can interact with JavaScript-rendered content
- More reliable for complex websites
- Can handle dynamic content loading

**Cons:**
- Slower (needs to load full browser)
- More resource-intensive
- Requires Chrome/Firefox driver

### Option 2: Use Alternative Data Sources

**Open-Source DDI Databases:**
1. **DrugBank** (https://go.drugbank.com) - Comprehensive drug database with API access
2. **RxNorm** + **RxNav** (https://rxnav.nlm.nih.gov) - NLM's drug interaction API
3. **SIDER** (http://sideeffects.embl.de) - Side effects and drug interactions
4. **DailyMed** (https://dailymed.nlm.nih.gov) - FDA drug labels with interaction info

**Example using RxNorm API:**
```python
import requests

drug1 = "207106"  # RxCUI for Lisinopril
drug2 = "153165"  # RxCUI for Amlodipine

url = f"https://rxnav.nlm.nih.gov/REST/interaction/interaction.json?rxcui={drug1}"
response = requests.get(url)
data = response.json()
```

### Option 3: Manual Data Collection

For an FYP with focus on ML implementation rather than data collection:
- Use existing published DDI datasets
- Manually compile a subset of critical interactions
- Focus resources on the ML model development

---

## 📁 Output Format

The scraper (once functional) will generate a CSV file with the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| Drug_1 | First drug name | "Amlodipine" |
| Drug_1_Class | Drug class of first drug | "CCBs" |
| Drug_2 | Second drug name | "Lisinopril" |
| Drug_2_Class | Drug class of second drug | "ACE Inhibitors" |
| Severity | Interaction severity | "Major" / "Moderate" / "Minor" / "None" |
| URL | Source URL for verification | "https://..." |
| Timestamp | When interaction was checked | "2025-11-23T14:30:00" |
| Status | Success or error message | "Success" |

---

## 🛠️ Files in This Repository

```
.
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── scrape_drug_interactions.py        # Main scraper (requires update for Selenium)
├── analyze_excel.py                   # Excel structure analyzer
├── DRUGS INTERACTION (HYPERTENSION).xlsx  # Input drug data
├── drug_interactions_results.csv      # Output (generated after scraping)
└── scraping_progress.json             # Auto-save progress file
```

---

## 🆕 UPDATE: Alternative Solutions (November 2025)

### Critical Discovery: RxNorm Interaction API Discontinued

As of January 2, 2024, the RxNorm Drug Interaction API has been discontinued by NIH. After extensive testing, we've identified the following working alternatives:

**✅ Working Solutions:**

1. **DDInter Database** (Recommended for quick start)
   - Free, academic-quality database with 302K+ interactions
   - Access: https://ddinter2.scbdd.com/
   - No authentication required
   - Can be accessed via web interface or downloads
   - See `DDI_DATA_COLLECTION_OPTIONS.md` for details

2. **Selenium-based Scraping** (For automated collection)
   - Bypasses JavaScript requirements on Drugs.com
   - Fully automated collection of all 2,556 pairs
   - Implementation available on request

3. **DrugBank API** (For publication-quality research)
   - Requires free academic license application
   - Gold standard drug interaction database
   - 1.3M+ interactions with detailed annotations

**📄 New Files:**
- `rxnorm_scraper.py` - RxNorm drug mapping (RxCUI lookup works!)
- `ddinter_collector.py` - DDInter database integration framework
- `DDI_DATA_COLLECTION_OPTIONS.md` - Complete analysis and recommendations

**⚡ Quick Start Recommendation:**
For immediate progress on your ML models, see the **Hybrid Approach** in `DDI_DATA_COLLECTION_OPTIONS.md`

---

## 📖 Technical Details

### Drug Extraction Logic

The script extracts drugs from specific Excel sheet locations:

- **Column C (ACE Inhibitors):** Rows 5-15
- **Column D (ARBs):** Rows 5-12
- **Columns E-F (CCBs):** Rows 6-15
- **Columns G-H (Diuretics):** Rows 5-15
- **Column I (Alpha Blockers):** Rows 5-10
- **Column J (Beta Blockers):** Rows 5-19

### Drug Name Cleaning

The script automatically:
- Removes suffixes like "SR", "XL", "ER"
- Strips parenthetical info like "(Thiazide diuretics)"
- Removes emojis and special characters
- Standardizes formatting

### Rate Limiting & Ethics

The scraper implements:
- **2-second delay** between requests (respectful to server)
- Custom User-Agent identifying academic research
- Progress auto-save to resume if interrupted
- Error handling and retry logic

---

## 🎯 Recommendations for Your FYP

Given the JavaScript limitation and your supervisors' preference to focus on ML implementation:

### Recommended Approach:
1. **Use RxNorm/DrugBank API** for initial dataset creation
2. **Implement Selenium version** if web scraping is specifically required
3. **Focus majority of time on ML models** (Random Forest, SVC, Naive Bayes)
4. **Document data collection challenges** in your thesis as learning outcomes

### Timeline Suggestion:
- **Week 1:** Finalize data collection method (API or Selenium)
- **Week 2:** Collect and clean data
- **Weeks 3-6:** ML model development and evaluation
- **Week 7:** Integration with Malaysian CPG guidelines
- **Week 8:** Documentation and presentation

---

## 📞 Next Steps - Choose Your Path

**Option A: Alternative DDI Data Sources (Recommended)**
- Faster and more reliable than web scraping
- RxNorm API provides structured, validated data
- Focus time on ML implementation

**Option B: Selenium-Based Scraper**
- Required if specifically need Drugs.com data
- More complex setup, slower execution
- Can be implemented if needed

**Option C: Hybrid Approach**
- Use API for bulk data collection
- Manually verify subset with Drugs.com
- Best balance of time and quality

---

## 📚 References

- Drugs.com Drug Interaction Checker
- RxNorm API Documentation: https://lhncbc.nlm.nih.gov/RxNav/APIs/
- DrugBank Documentation: https://docs.drugbank.com/
- Malaysian Clinical Practice Guidelines for Hypertension

---

## 👨‍💻 Author

**Final Year Project Student**
University of Malaya
Supervisors: Unaizah, Nurulhuda

---

## 📄 License

This code is for academic research purposes as part of a Final Year Project at University of Malaya. Please respect Drugs.com's terms of service and robots.txt when conducting web scraping activities.