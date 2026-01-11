# Machine Learning-Driven Prediction for Safe Medication Pathways among Hypertensive Patients

**Final Year Project - University of Malaya**

**Supervisor:** Dr. Unaizah Hanum Obeidellah
**Collaborator:** Dr Nurulhuda Abdul Manaf (UPNM)
**Student:** Jonathan Siew Zunxian

---

## Project Overview

Hypertension is one of the most prevalent chronic diseases in Malaysia, particularly among patients who are prescribed multiple medications simultaneously. This increases the risk of inappropriate prescribing and drug–drug interactions (DDIs), which can lead to serious adverse events such as kidney failure, hypoglycemia, and cardiovascular complications. Despite the availability of Malaysian Clinical Practice Guidelines (CPGs), there is limited systematic analysis of prescribing patterns and DDIs in hypertensive patients in Malaysia.

This project aims to address this gap by leveraging machine learning techniques to identify inappropriate prescriptions and through predicting the optimal medication pathway, ultimately supporting safer prescribing decisions.

### Project Objectives

1. Identify common drug classes prescribed to hypertension patients
2. Assess the prevalence of potential DDIs using standard interaction checkers
3. Propose a safer medication pathway aligned with local guidelines

The study will focus on medications consumed by hypertensive patients using data derived from Malaysian CPGs. Through literature review, drug interaction analysis, and data-driven modeling, the project aims to recommend optimized treatment pathways. The expected outcome is a data-informed framework that supports clinicians in reducing medication errors and improving patient safety in Malaysian healthcare settings.

---

## Drug Classes and Medications

The project analyzes interactions between 29 hypertension medications across 5 major drug classes:

| Drug Class | Count | Medications |
|-----------|-------|-------------|
| **ACE Inhibitors (ACEI)** | 6 | Captopril, Enalapril, Lisinopril, Perindopril, Ramipril, Imidapril |
| **Angiotensin Receptor Blockers (ARB)** | 6 | Candesartan, Irbesartan, Losartan, Telmisartan, Valsartan, Olmesartan |
| **Beta Blockers** | 7 | Acebutolol, Atenolol, Betaxolol, Bisoprolol, Metoprolol, Nebivolol, Propranolol |
| **Calcium Channel Blockers (CCB)** | 7 | Amlodipine, Felodipine, Isradipine, Lercanidipine, Nifedipine, Diltiazem, Verapamil |
| **Diuretics** | 3 | Hydrochlorothiazide, Indapamide, Amiloride |

**Total drug pairs analyzed:** 406 unique combinations

---

## Repository Structure

### Core Data Files

- **FYP_Drug_Interaction_Template.csv** - Template file containing all 406 drug pair combinations with columns for data collection
- **FYP_Drug_Interaction_Final.csv** - Completed dataset with interaction data from both sources

### Data Collection Scripts

#### Primary Scrapers

1. **drugbank_ddi_scraper.py**
   - Playwright-based scraper for DrugBank DDI Checker (dev.drugbank.com/demo/ddi_checker)
   - Automated browser interaction with anti-detection measures
   - Extracts severity levels (Major/Moderate/Minor/None) and interaction descriptions
   - Checkpoint system for resumable scraping
   - Usage: `python drugbank_ddi_scraper.py FYP_Drug_Interaction_Template.csv`

2. **playwright_ddi_scraper.py**
   - Playwright-based scraper for Drugs.com interaction checker
   - Header Guard logic to distinguish drug-drug interactions from food/disease interactions
   - Robust extraction with multiple fallback strategies
   - Checkpoint system for resumable scraping
   - Usage: `python playwright_ddi_scraper.py FYP_Drug_Interaction_Template.csv`

#### Utility Scripts

3. **create_sample_drug_pairs.py**
   - Generates the drug pair template CSV file from predefined drug lists
   - Creates 406 unique drug pair combinations
   - Includes placeholder columns for data collection (DrugsCom_Severity, DrugBank_Severity, etc.)

4. **update_drugscom_severity.py**
   - Post-processing script to standardize severity values
   - Updates "No drug-drug interactions found" entries to "None" severity level
   - Ensures data consistency across the dataset

#### Shell Scripts

5. **run_drugbank_scraper.sh**
   - Interactive menu system for DrugBank scraper
   - Options for full scraping, testing (5 rows), and debugging
   - Automated environment setup and dependency checking

6. **run_playwright_scraper.sh**
   - Interactive menu system for Drugs.com scraper
   - Options for creating sample files and running scraper
   - Automated environment setup and dependency checking

### Debug Scripts

The project includes six debug scripts for troubleshooting scraper issues:

- **debug_drugbank_page_load.py** - Tests DrugBank page loading and structure
- **debug_drugbank_add_drugs.py** - Tests adding drugs to DrugBank interface
- **debug_drugbank_html_analysis.py** - Analyzes saved HTML from DrugBank
- **debug_page_load.py** - Tests Drugs.com page loading and structure
- **debug_add_drugs.py** - Tests adding drugs to Drugs.com interface
- **debug_html_analysis.py** - Analyzes saved HTML from Drugs.com

### Configuration

- **requirements.txt** - Python package dependencies

---

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)
- Internet connection for web scraping

### Installation

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers
playwright install chromium
```

---

## Usage

### Quick Start with Shell Scripts

#### For DrugBank Scraping:
```bash
bash run_drugbank_scraper.sh
```

This provides an interactive menu with options:
1. Run scraper on full dataset
2. Test scraper with first 5 rows
3. Debug page structure
4. Debug drug addition
5. Analyze saved HTML files

#### For Drugs.com Scraping:
```bash
bash run_playwright_scraper.sh
```

### Manual Execution

#### Create Drug Pair Template
```bash
python create_sample_drug_pairs.py
```

This generates `FYP_Drug_Interaction_Template.csv` with 406 drug pairs.

#### Run DrugBank Scraper
```bash
# Full scraping
python drugbank_ddi_scraper.py FYP_Drug_Interaction_Template.csv

# Test mode (first 5 rows)
python drugbank_ddi_scraper.py FYP_Drug_Interaction_Template.csv --start 0 --end 5

# Custom range
python drugbank_ddi_scraper.py FYP_Drug_Interaction_Template.csv --start 0 --end 100

# Custom output file
python drugbank_ddi_scraper.py FYP_Drug_Interaction_Template.csv --output results.csv

# Adjust delay between requests (default: 2.5 seconds)
python drugbank_ddi_scraper.py FYP_Drug_Interaction_Template.csv --delay 3.0
```

#### Run Drugs.com Scraper
```bash
# Full scraping
python playwright_ddi_scraper.py FYP_Drug_Interaction_Template.csv

# With custom output
python playwright_ddi_scraper.py FYP_Drug_Interaction_Template.csv --output results.csv

# Adjust delay between requests (default: 3.5 seconds)
python playwright_ddi_scraper.py FYP_Drug_Interaction_Template.csv --delay 4.0
```

#### Post-Processing
```bash
# Standardize severity values
python update_drugscom_severity.py
```

---

## Data Collection Workflow

1. **Generate Template**
   - Run `create_sample_drug_pairs.py` to create the drug pair template

2. **Scrape DrugBank Data**
   - Run `drugbank_ddi_scraper.py` to collect data from DrugBank
   - Populates `DrugBank_Severity` and `DrugBank_Text` columns

3. **Scrape Drugs.com Data**
   - Run `playwright_ddi_scraper.py` to collect data from Drugs.com
   - Populates `DrugsCom_Severity` and `DrugsCom_Text` columns

4. **Post-Process Data**
   - Run `update_drugscom_severity.py` to standardize severity values
   - Manual review of conflicts between sources

5. **Finalize Ground Truth**
   - Review and resolve discrepancies between DrugBank and Drugs.com
   - Populate `Final_Severity` column for ML model training

---

## CSV Template Structure

The template CSV contains the following columns:

| Column | Type | Description |
|--------|------|-------------|
| Drug_A_Name | String | First drug name |
| Drug_B_Name | String | Second drug name |
| Drug_A_Class | String | First drug class (ACEI, ARB, Beta-Blocker, CCB, Diuretic) |
| Drug_B_Class | String | Second drug class |
| DrugsCom_Severity | String | Severity from Drugs.com (Major/Moderate/Minor/None/TBD) |
| DrugsCom_Text | String | Interaction description from Drugs.com |
| DrugBank_Severity | String | Severity from DrugBank (Major/Moderate/Minor/None/TBD) |
| DrugBank_Text | String | Interaction description from DrugBank |
| Final_Severity | String | Ground truth severity for ML model (to be determined after review) |
| Risk_Score | Float | Numeric risk score (0.2 for Major to 1.0 for None) |

---

## Scraper Features

### DrugBank Scraper (drugbank_ddi_scraper.py)

- **Anti-Detection Measures:** Masked automation, realistic user agent, human-like delays
- **Smart Drug Selection:** Fuzzy matching algorithm to select correct dropdown options
- **Multiple Extraction Strategies:** Fallback methods for robust data extraction
- **Checkpoint System:** Auto-saves progress every 10 rows, resumable after interruption
- **Debug Mode:** Saves screenshots and HTML for troubleshooting
- **Configurable Delays:** Minimum 2-second delay between requests (default: 2.5s)

### Drugs.com Scraper (playwright_ddi_scraper.py)

- **Header Guard Logic:** Specifically targets "Interactions between your drugs" section
- **Anti-Detection Measures:** Masked automation, realistic browser behavior
- **Robust Extraction:** Multiple fallback strategies for severity and text extraction
- **Checkpoint System:** Auto-saves progress every 10 rows, resumable after interruption
- **Debug Mode:** Saves screenshots and HTML for troubleshooting
- **Configurable Delays:** Minimum 3-second delay between requests (default: 3.5s)

---

## Rate Limiting and Ethics

Both scrapers implement responsible web scraping practices:

- **Respectful Delays:** 2.5-3.5 second delays between requests (configurable)
- **Random Intervals:** Human-like variation in request timing
- **Progress Checkpoints:** Avoids re-scraping already processed pairs
- **User-Agent Headers:** Identifies as academic research project
- **Error Handling:** Graceful failure with detailed logging

---

## Logging and Debugging

### Log Files

- **drugbank_scraper.log** - Detailed logs for DrugBank scraper
- **playwright_ddi_scraper.log** - Detailed logs for Drugs.com scraper

### Checkpoint Files

- **ddi_checkpoint_drugbank.csv** - Progress checkpoint for DrugBank scraper
- **ddi_checkpoint.csv** - Progress checkpoint for Drugs.com scraper

### Debug Output

When errors occur, scrapers automatically save:
- Full-page screenshots (PNG)
- Complete HTML source (HTML)
- Timestamped filenames for easy identification

---

## Known Issues and Limitations

1. **JavaScript Requirement:** Both sources require browser automation; simple HTTP requests cannot access interaction data
2. **Rate Limiting:** Respectful delays mean full dataset collection takes several hours
3. **Selector Fragility:** Website structure changes may require selector updates
4. **Network Dependency:** Requires stable internet connection
5. **Data Conflicts:** DrugBank and Drugs.com may report different severity levels for the same pair

---

## Machine Learning Pipeline (Next Steps)

After data collection, the project will:

1. **Data Cleaning and Validation**
   - Resolve conflicts between DrugBank and Drugs.com
   - Establish ground truth `Final_Severity` values
   - Calculate `Risk_Score` numeric values

2. **Feature Engineering**
   - Drug class combinations
   - Pharmacological properties
   - Malaysian CPG guideline alignment

3. **Model Development**
   - Random Forest Classifier
   - Support Vector Classifier (SVC)
   - Naive Bayes Classifier

4. **Evaluation and Validation**
   - Cross-validation
   - Confusion matrix analysis
   - Feature importance analysis

5. **Clinical Integration**
   - Recommendation system aligned with Malaysian CPG
   - Risk stratification framework
   - Safer medication pathway suggestions

---

## Dependencies

See `requirements.txt` for complete list. Key packages:

- **pandas** - Data manipulation and CSV handling
- **openpyxl** - Excel file support
- **playwright** - Browser automation for web scraping
- **beautifulsoup4** - HTML parsing
- **selenium** - Alternative browser automation (legacy)
- **requests** - HTTP requests
- **lxml** - XML/HTML processing

---

## References

- Malaysian Clinical Practice Guidelines for Hypertension
- DrugBank Database: https://dev.drugbank.com/demo/ddi_checker
- Drugs.com Drug Interaction Checker: https://www.drugs.com/drug_interactions.html
- MIMS Malaysia 2018

---

## License

This project is for academic research purposes as part of a Final Year Project at University of Malaya. Data collection is conducted in accordance with website terms of service and robots.txt policies. The collected data is used solely for educational and research purposes.

---

## Contact

For questions or collaboration inquiries, please contact the project supervisor:

**Dr. Unaizah Hanum Obeidellah**
Faculty of Computer Science and Information Technology
University of Malaya

---

## Acknowledgments

Special thanks to Dr. Nurulhuda Abdul Manaf (UPNM) for clinical expertise and collaboration, and to the University of Malaya for supporting this research project.
