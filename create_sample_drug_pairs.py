import pandas as pd
from itertools import combinations

# 1. Define the Official Drug List (From MIMS Tables)
drugs = {
    "ACEI": ["Captopril", "Enalapril", "Lisinopril", "Perindopril", "Ramipril", "Imidapril"],
    "ARB": ["Candesartan", "Irbesartan", "Losartan", "Telmisartan", "Valsartan", "Olmesartan"],
    "Beta-Blocker": ["Acebutolol", "Atenolol", "Betaxolol", "Bisoprolol", "Metoprolol", "Nebivolol", "Propranolol"],
    "CCB": ["Amlodipine", "Felodipine", "Isradipine", "Lercanidipine", "Nifedipine", "Diltiazem", "Verapamil"],
    "Diuretic": ["Hydrochlorothiazide", "Indapamide", "Amiloride"]
}

# 2. Flatten List
all_drugs = []
for category, drug_list in drugs.items():
    for drug in drug_list:
        all_drugs.append({"Name": drug, "Class": category})

# 3. Generate Pairs
drug_pairs = list(combinations(all_drugs, 2))

# 4. Create the Final DataFrame Structure
data = []
for drug_a, drug_b in drug_pairs:
    data.append({
        # Identity
        "Drug_A_Name": drug_a["Name"],
        "Drug_B_Name": drug_b["Name"],
        "Drug_A_Class": drug_a["Class"],
        "Drug_B_Class": drug_b["Class"],

        # Scraped Data (Initialize as Empty/TBD)
        "DrugsCom_Severity": "TBD",
        "DrugsCom_Text": "TBD",
        "DrugBank_Severity": "TBD",
        "DrugBank_Text": "TBD",

        # Targets (To be computed after scraping)
        "Final_Severity": "TBD",
        "Risk_Score": 0.0
    })

df = pd.DataFrame(data)

# 5. Save
filename = "FYP_Drug_Interaction_Dataset_Template.csv"
df.to_csv(filename, index=False)

print(f"Dataset template created with {len(df)} rows.")
print(f"Columns: {list(df.columns)}")
