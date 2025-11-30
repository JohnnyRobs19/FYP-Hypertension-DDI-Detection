import pandas as pd
from itertools import combinations

# ==========================================
# 1. DEFINE OFFICIAL DRUG LIST (Malaysian CPG / MIMS 2018)
# ==========================================
drugs = {
    "ACEI": ["Captopril", "Enalapril", "Lisinopril", "Perindopril", "Ramipril", "Imidapril"],
    "ARB": ["Candesartan", "Irbesartan", "Losartan", "Telmisartan", "Valsartan", "Olmesartan"],
    "Beta-Blocker": ["Acebutolol", "Atenolol", "Betaxolol", "Bisoprolol", "Metoprolol", "Nebivolol", "Propranolol"],
    # Note: We group them as CCB here, but remember Diltiazem/Verapamil are Non-Dihydro (Heart rate risks)
    "CCB": ["Amlodipine", "Felodipine", "Isradipine", "Lercanidipine", "Nifedipine", "Diltiazem", "Verapamil"],
    "Diuretic": ["Hydrochlorothiazide", "Indapamide", "Amiloride"]
}

# ==========================================
# 2. FLATTEN LIST & GENERATE PAIRS
# ==========================================
all_drugs = []
for category, drug_list in drugs.items():
    # Clean class names (optional, but good for consistency)
    clean_class = "CCB" if "CCB" in category else category
    for drug in drug_list:
        all_drugs.append({"Name": drug, "Class": clean_class})

# Generate all unique pairs.
# This INCLUDES "Bad" pairs (ACEI+ARB) and "Duplication" pairs (ACEI+ACEI).
drug_pairs = list(combinations(all_drugs, 2))

# ==========================================
# 3. CREATE FINAL DATAFRAME
# ==========================================
data = []
for drug_a, drug_b in drug_pairs:
    data.append({
        # --- IDENTITY ---
        "Drug_A_Name": drug_a["Name"],
        "Drug_B_Name": drug_b["Name"],
        "Drug_A_Class": drug_a["Class"],
        "Drug_B_Class": drug_b["Class"],

        # --- VALIDATION DATA (To be Scraped) ---
        "DrugsCom_Severity": "TBD",   # Major/Moderate/Minor/None
        "DrugsCom_Text": "TBD",       # <--- ADDED: Helps you verify conflicts manually
        "DrugBank_Severity": "TBD",   # Major/Moderate/Minor/None
        "DrugBank_Text": "TBD",       # <--- ADDED: Helps you verify conflicts manually

        # --- MODEL TARGETS ---
        "Final_Severity": "TBD",      # The Ground Truth for your ML Model
        "Risk_Score": 0.0             # 0.2 (Major) to 1.0 (None) for Math Model
    })

df = pd.DataFrame(data)

# ==========================================
# 4. VERIFICATION & EXPORT
# ==========================================
# Verify "Same Class" pairs exist (e.g. Captopril + Enalapril)
same_class_count = len(df[df['Drug_A_Class'] == df['Drug_B_Class']])
acei_arb_count = len(df[((df['Drug_A_Class'] == 'ACEI') & (df['Drug_B_Class'] == 'ARB')) | ((df['Drug_A_Class'] == 'ARB') & (df['Drug_B_Class'] == 'ACEI'))])

print(f"✅ Template Generated Successfully")
print(f"Total Pairs: {len(df)}")
print(f"Duplication Checks (Same Class) Included: {same_class_count}")
print(f"Major Interaction Checks (ACEI+ARB) Included: {acei_arb_count}")

# Save the file - THIS is the file your Scraper will read
df.to_csv("FYP_Drug_Interaction_Template.csv", index=False)
print("File saved as: FYP_Drug_Interaction_Template.csv")
