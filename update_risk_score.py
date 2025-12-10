#!/usr/bin/env python3
"""
Update Risk_Score from 0.2 to 0.25 for rows where Final_Severity is 'Major'
"""
import pandas as pd

# Read the CSV file
df = pd.read_csv('FYP_Drug_Interaction_Final.csv')

# Count rows before update
major_rows_before = df[df['Final_Severity'] == 'Major'].shape[0]
risk_020_rows = df[(df['Final_Severity'] == 'Major') & (df['Risk_Score'] == 0.2)].shape[0]

print(f"Total rows with Final_Severity = 'Major': {major_rows_before}")
print(f"Rows with Risk_Score = 0.2 that will be updated: {risk_020_rows}")

# Update Risk_Score from 0.2 to 0.25 where Final_Severity is 'Major'
df.loc[df['Final_Severity'] == 'Major', 'Risk_Score'] = 0.25

# Count rows after update
risk_025_rows = df[(df['Final_Severity'] == 'Major') & (df['Risk_Score'] == 0.25)].shape[0]

print(f"\nAfter update:")
print(f"Rows with Risk_Score = 0.25 (Major severity): {risk_025_rows}")

# Save the updated CSV
df.to_csv('FYP_Drug_Interaction_Final.csv', index=False)

print(f"\n✓ Successfully updated FYP_Drug_Interaction_Final.csv")
print(f"✓ Changed Risk_Score from 0.2 to 0.25 for {risk_020_rows} rows")
