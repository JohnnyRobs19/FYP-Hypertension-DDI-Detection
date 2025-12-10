#!/usr/bin/env python3
"""
Fix Severity Values: Ensure "None" strings are used instead of empty/NaN values

This script fixes the DrugsCom_Severity and DrugBank_Severity columns to use
the string "None" for cases where no drug interaction was found, instead of
leaving them as empty strings or NaN values.

This maintains data consistency with the project's standards.
"""

import pandas as pd

# Read the CSV
df = pd.read_csv('FYP_Drug_Interaction_Final.csv')

print("="*80)
print("FIXING SEVERITY VALUES")
print("="*80)

# Count current state
print("\nBEFORE:")
print(f"DrugsCom_Severity - NaN/empty count: {df['DrugsCom_Severity'].isna().sum()}")
print(f"DrugBank_Severity - NaN/empty count: {df['DrugBank_Severity'].isna().sum()}")

# Fix DrugsCom_Severity
# Set to "None" when DrugsCom_Text is "No drug-drug interactions found"
drugscom_fix_count = 0
for idx, row in df.iterrows():
    if pd.isna(row['DrugsCom_Severity']) or row['DrugsCom_Severity'] == '':
        if row['DrugsCom_Text'] == 'No drug-drug interactions found':
            df.at[idx, 'DrugsCom_Severity'] = 'None'
            drugscom_fix_count += 1

# Fix DrugBank_Severity
# Set to "None" when DrugBank_Text indicates no interaction
drugbank_fix_count = 0
for idx, row in df.iterrows():
    if pd.isna(row['DrugBank_Severity']) or row['DrugBank_Severity'] == '':
        # Check if DrugBank_Text indicates no interaction or is empty/error
        text = str(row['DrugBank_Text'])
        if ('No interaction' in text or
            text == 'nan' or
            text == '' or
            'Error:' in text or
            'Timeout' in text):
            df.at[idx, 'DrugBank_Severity'] = 'None'
            drugbank_fix_count += 1

print(f"\nFixed {drugscom_fix_count} DrugsCom_Severity values")
print(f"Fixed {drugbank_fix_count} DrugBank_Severity values")

# Count after
print("\nAFTER:")
print(f"DrugsCom_Severity - NaN/empty count: {df['DrugsCom_Severity'].isna().sum()}")
print(f"DrugsCom_Severity - 'None' count: {(df['DrugsCom_Severity'] == 'None').sum()}")
print(f"DrugBank_Severity - NaN/empty count: {df['DrugBank_Severity'].isna().sum()}")
print(f"DrugBank_Severity - 'None' count: {(df['DrugBank_Severity'] == 'None').sum()}")

# Save with proper handling of None strings
print("\nSaving to FYP_Drug_Interaction_Final.csv...")
df.to_csv('FYP_Drug_Interaction_Final.csv', index=False, na_rep='')

print("\n" + "="*80)
print("COMPLETED")
print("="*80)
print("Severity columns now use 'None' string for no interactions")
