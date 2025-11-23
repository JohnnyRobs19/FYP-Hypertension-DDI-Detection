# Drug-Drug Interaction Data Collection Options for Your FYP

## 🔍 Situation Summary

After thorough investigation, here's what we discovered:

### What We Tried:
1. ✅ **RxNorm API** - Drug name lookup works great (mapped 72 drugs to RxCUIs)
2. ❌ **RxNorm Interaction API** - **Discontinued on January 2, 2024**
3. ✅ **DDInter Database** - Free, comprehensive, but download structure is complex
4. 🔐 **DrugBank** - Requires license application (free for academic use, but application process)

---

## 📊 Available Options for Your Project

### Option 1: Use Drugs.com with Selenium ⭐ **RECOMMENDED FOR AUTOMATED COLLECTION**

**Pros:**
- Complete, reliable interaction data
- Severity ratings (Major, Moderate, Minor)
- Can collect all 2,556 drug pairs automatically
- Verified data source trusted by healthcare professionals

**Cons:**
- Requires Selenium setup (~30 mins)
- Takes 2-3 hours to collect all interactions
- More complex code

**Implementation:**
```bash
# Install Selenium
pip install selenium webdriver-manager

# Run the script (to be created)
python selenium_scraper.py
```

**Estimated Time:** 1 hour setup + 2-3 hours data collection = **3-4 hours total**

---

### Option 2: Manual DDInter Database Access ⭐ **QUICKEST START**

**Pros:**
- Free, no authentication needed
- Already has 302,516 drug-drug interactions
- Can start immediately via web interface
- Academic-quality data

**Cons:**
- Need to manually search each interaction pair OR figure out therapeutic area downloads
- Downloads organized by ATC therapeutic codes (cardiovascular section for hypertension)

**Implementation:**
1. Visit: https://ddinter.scbdd.com/ or https://ddinter2.scbdd.com/
2. Use the search interface to look up pairs
3. Or download cardiovascular section from http://ddinter.scbdd.com/download/

**Estimated Time:** Manual search of sample pairs: **30 mins - 2 hours**

---

### Option 3: Apply for DrugBank Academic License 🎓

**Pros:**
- Gold standard drug database
- 1.3M drug-drug interactions
- Official API access
- Best for publishable research

**Cons:**
- Requires application and approval
- May take days/weeks to get approved
- Learning curve for API

**Implementation:**
1. Apply at https://go.drugbank.com/
2. Wait for academic license approval
3. Use their API

**Estimated Time:** **1-2 weeks** (waiting for approval) + 2 hours implementation

---

### Option 4: Hybrid Approach - Sample Data Collection ⚡ **FASTEST TO ML MODELS**

**Pros:**
- Get started on ML immediately
- Focus on model development (your supervisors' priority)
- Can collect more data later if needed

**Cons:**
- Smaller dataset initially
- May need to expand later

**Implementation:**
1. Manually collect 100-200 key interactions from DDInter or Drugs.com
2. Focus on common combinations (ACE+Diuretics, CCB+Beta Blockers, etc.)
3. Start ML model development
4. Expand dataset as needed

**Estimated Time:** **2-4 hours** to get started with ML

---

## 🎯 My Recommendation for Your FYP

Given your supervisors (Unaizah & Nurulhuda) want focus on **ML implementation**, I recommend:

### **Recommended Path: Hybrid Approach → Option 4**

#### Week 1 Actions:
1. **TODAY (30 mins):** Manually collect 50-100 critical drug interactions from DDInter
   - Focus on most prescribed combinations
   - Document interaction levels and descriptions

2. **This Week (2 hours):** Clean and format data into CSV
   - Columns: Drug1, Class1, Drug2, Class2, Severity, Description
   - Create training/test split

3. **Next Week:** Start ML model development
   - Random Forest
   - SVC
   - Naive Bayes

4. **Later (if needed):** Implement Selenium scraper for complete dataset

---

## 🛠️ Ready-to-Use Scripts I've Created

### Files Ready in Your Directory:

1. **`scrape_drug_interactions.py`**
   - Original web scraper (requires Selenium update)
   - 72 drugs extracted successfully
   - 2,556 combinations generated

2. **`rxnorm_scraper.py`** ✅
   - Works for drug name → RxCUI mapping
   - Successfully tested with your drugs
   - Interaction API unavailable (discontinued)

3. **`ddinter_collector.py`**
   - Download framework created
   - Needs adjustment for correct DDInter URLs
   - Can be fixed if you want automated DDInter access

### What You Can Do RIGHT NOW:

```bash
# Option A: Test RxNorm drug mapping (works!)
source venv/bin/activate
python rxnorm_scraper.py test

# Option B: Extract your 72 drugs and see combinations
python scrape_drug_interactions.py dry-run

# Option C: Manually create initial dataset
# Create a CSV file with structure:
# Drug_1,Drug_1_Class,Drug_2,Drug_2_Class,Severity,Description
```

---

## 📝 Quick Start Template for Manual Collection

Here's a starter CSV you can fill in manually from DDInter:

```csv
Drug_1,Drug_1_Class,Drug_2,Drug_2_Class,Severity,Description,Source
Lisinopril,ACE Inhibitors,Hydrochlorothiazide,Diuretics,Moderate,May increase risk of hypotension,DDInter
Amlodipine,CCBs,Metoprolol,Beta Blockers,Moderate,May increase risk of bradycardia,DDInter
Losartan,ARBs,Spironolactone,Diuretics,Major,May increase risk of hyperkalemia,DDInter
... (add more as you find them)
```

---

## ⏱️ Timeline Comparison

| Approach | Setup Time | Data Collection | Total to ML | Dataset Size |
|----------|-----------|-----------------|-------------|--------------|
| **Hybrid (Recommended)** | 30 mins | 2-4 hours | **2-4 hours** | 50-200 interactions |
| Selenium | 1 hour | 2-3 hours | 3-4 hours | 2,556 interactions |
| DrugBank API | 2 hours | 1 hour | 1-2 weeks* | Full database |
| Manual DDInter | 0 mins | 5-10 hours | 5-10 hours | 2,556 interactions |

*Includes waiting for license approval

---

## 💡 Next Steps - Choose Your Path

### If you want to start ML work TODAY:
→ **Use Option 4 (Hybrid Approach)**
1. Visit https://ddinter2.scbdd.com/
2. Search for 50-100 key drug combinations
3. Record results in CSV
4. Start building your Random Forest model

### If you want complete automated dataset:
→ **Use Option 1 (Selenium)**
1. Let me create the Selenium scraper for you
2. Run it overnight
3. Have complete dataset tomorrow

### If you want academic gold standard:
→ **Use Option 3 (DrugBank)**
1. Apply for academic license today
2. Work on Option 4 while waiting
3. Switch to DrugBank data when approved

---

## 📚 Resources

### DDInter Database:
- **Version 1.0:** http://ddinter.scbdd.com/
- **Version 2.0:** https://ddinter2.scbdd.com/
- **Download Page:** http://ddinter.scbdd.com/download/
- **License:** CC-BY-NC-SA (Free for academic use)

### Reference Papers:
- [DDInter 2.0 Paper](https://academic.oup.com/nar/article/53/D1/D1356/7740584) - Latest version
- [Original DDInter Paper](https://academic.oup.com/nar/article/50/D1/D1200/6389535)

### Other Resources:
- [DrugBank Clinical](https://go.drugbank.com/clinical)
- [RxNorm Documentation](https://lhncbc.nlm.nih.gov/RxNav/)

---

## 🤝 What I Can Do Next

**Choose one:**

### A. "Create Selenium Scraper"
I'll build a complete Selenium-based scraper for Drugs.com that will:
- Automatically check all 2,556 combinations
- Extract severity and descriptions
- Save to CSV with progress tracking

### B. "Help with Manual Collection"
I'll create a web scraping helper that:
- Opens DDInter for each drug pair
- Guides you through manual collection
- Formats data automatically

### C. "Start with Sample Data"
I'll create a starter dataset with:
- 50-100 manually researched interactions
- Properly formatted for ML
- Documentation for expanding later

---

## ❓ Questions to Discuss with Supervisors

Before proceeding, consider asking Unaizah & Nurulhuda:

1. **Is Drugs.com specifically required as data source?**
   - If yes → Selenium approach
   - If no → DDInter is faster and academic-quality

2. **What's the minimum dataset size for the ML models?**
   - Small (50-200) → Manual/Hybrid approach fine
   - Large (1000+) → Automated approach needed

3. **How much time should be spent on data collection vs ML?**
   - Minimal data collection time → Hybrid approach
   - Complete dataset priority → Selenium or DrugBank

4. **Do you need to document the data collection methodology?**
   - If yes → Selenium has good documentation story
   - If no → Whatever works fastest

---

## 🎯 My Final Recommendation

**Start with the Hybrid Approach:**

1. **TODAY:** Spend 1-2 hours manually collecting 50-100 interactions from DDInter 2.0
2. **THIS WEEK:** Build your first ML model with this data
3. **NEXT WEEK:** If you need more data, we'll implement the Selenium scraper

This way:
- ✅ You make immediate progress on ML (supervisors' priority)
- ✅ You demonstrate data collection methodology
- ✅ You have flexibility to expand later
- ✅ You're not blocked waiting for API approvals

---

**Ready to proceed? Let me know which option you choose and I'll help you implement it!**
