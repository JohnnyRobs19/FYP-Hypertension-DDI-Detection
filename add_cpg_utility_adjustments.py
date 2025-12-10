#!/usr/bin/env python3
"""
Add CPG-Based Utility Adjustments to Drug Interaction Dataset

This script incorporates Malaysian Clinical Practice Guidelines (CPG) recommendations
into the drug interaction risk scoring system by adding utility adjustments based on:

1. Outcome Superiority: Diuretics like Indapamide show superior cardiovascular outcomes
2. Tolerability/Adherence: ACEIs have higher cough incidence than ARBs

Reference: Malaysian CPG for Management of Hypertension (5th Edition)
"""

import pandas as pd
import sys
from pathlib import Path

# CPG-based adjustment values (from Malaysian CPG)
OUTCOME_BONUS = 0.05  # For Indapamide (superior to HCTZ in CV outcomes)
TOLERABILITY_PENALTY = -0.01  # For ACEIs (higher cough incidence)

def check_drug_in_pair(row, drug_name):
    """Check if a specific drug is in the pair (Drug_A or Drug_B)"""
    return (row['Drug_A_Name'] == drug_name or
            row['Drug_B_Name'] == drug_name)

def check_class_in_pair(row, drug_class):
    """Check if a specific drug class is in the pair"""
    return (row['Drug_A_Class'] == drug_class or
            row['Drug_B_Class'] == drug_class)

def calculate_cpg_adjustments(df):
    """
    Calculate CPG-based utility adjustments for each drug pair.

    Args:
        df: DataFrame with drug interaction data

    Returns:
        DataFrame with added CPG adjustment columns
    """

    # 1. OUTCOME SUPERIORITY BONUS
    # CPG Citation: Page 102, Section 9.1 DIURETICS
    # "Indapamide and Chlorthalidone are superior to HCTZ in preventing CV events"
    df['CPG_Outcome_Bonus'] = df.apply(
        lambda row: OUTCOME_BONUS if check_drug_in_pair(row, 'Indapamide') else 0.0,
        axis=1
    )

    # 2. TOLERABILITY/ADHERENCE PENALTY
    # CPG Citation: Page 105, under the ARBS section
    # "ARBs have a lower incidence of cough than ACEIs"
    df['CPG_Tolerability_Penalty'] = df.apply(
        lambda row: TOLERABILITY_PENALTY if check_class_in_pair(row, 'ACEI') else 0.0,
        axis=1
    )

    # 3. CALCULATE ADJUSTED RISK SCORE
    # Base approach: Higher score = lower risk (safer combination)
    # Apply all relevant adjustments
    df['CPG_Adjusted_Risk_Score'] = (
        df['Risk_Score'] +
        df['CPG_Outcome_Bonus'] +
        df['CPG_Tolerability_Penalty']
    )

    return df

def main():
    """Main execution function"""

    # File paths
    input_file = 'FYP_Drug_Interaction_Final.csv'
    output_file = 'FYP_Drug_Interaction_Final.csv'
    backup_file = 'FYP_Drug_Interaction_Final_backup.csv'

    print("="*80)
    print("CPG Utility Adjustment Script")
    print("="*80)
    print(f"\nInput file: {input_file}")

    # Check if file exists
    if not Path(input_file).exists():
        print(f"Error: {input_file} not found!")
        sys.exit(1)

    # Read the dataset
    # Note: keep_default_na=False prevents "None" strings from being converted to NaN
    print(f"\nReading dataset...")
    df = pd.read_csv(input_file, keep_default_na=False, na_values=[''])
    print(f"Loaded {len(df)} drug pairs")

    # Show current columns
    print(f"\nCurrent columns: {list(df.columns)}")

    # Remove old CPG columns if they exist
    cpg_columns = [col for col in df.columns if col.startswith('CPG_')]
    if cpg_columns:
        print(f"\nRemoving old CPG columns: {cpg_columns}")
        df = df.drop(columns=cpg_columns)

    # Backup the original file
    print(f"\nCreating backup: {backup_file}")
    df.to_csv(backup_file, index=False)

    # Calculate CPG adjustments
    print("\nCalculating CPG-based utility adjustments...")
    df = calculate_cpg_adjustments(df)

    # Generate summary statistics
    print("\n" + "="*80)
    print("ADJUSTMENT SUMMARY")
    print("="*80)

    print(f"\n1. OUTCOME SUPERIORITY (Indapamide Bonus: +{OUTCOME_BONUS})")
    print(f"   - Pairs with Indapamide: {(df['CPG_Outcome_Bonus'] > 0).sum()}")

    print(f"\n2. TOLERABILITY/ADHERENCE (ACEI Penalty: {TOLERABILITY_PENALTY})")
    print(f"   - Pairs with ACEI: {(df['CPG_Tolerability_Penalty'] < 0).sum()}")

    print("\n3. RISK SCORE STATISTICS")
    print(f"   - Original Risk Score range: [{df['Risk_Score'].min():.2f}, {df['Risk_Score'].max():.2f}]")
    print(f"   - Adjusted Risk Score range: [{df['CPG_Adjusted_Risk_Score'].min():.2f}, {df['CPG_Adjusted_Risk_Score'].max():.2f}]")
    print(f"   - Mean adjustment: {(df['CPG_Adjusted_Risk_Score'] - df['Risk_Score']).mean():.4f}")

    # Show some examples
    print("\n" + "="*80)
    print("EXAMPLE ADJUSTMENTS")
    print("="*80)

    # Example 1: Indapamide pair
    indapamide_examples = df[df['CPG_Outcome_Bonus'] > 0].head(3)
    if not indapamide_examples.empty:
        print("\nExample - Indapamide pairs (Outcome Superiority):")
        for idx, row in indapamide_examples.iterrows():
            print(f"  {row['Drug_A_Name']} + {row['Drug_B_Name']}: "
                  f"Risk {row['Risk_Score']:.2f} → {row['CPG_Adjusted_Risk_Score']:.2f} "
                  f"(+{row['CPG_Outcome_Bonus']:.2f})")

    # Example 2: ACEI pair
    acei_examples = df[df['CPG_Tolerability_Penalty'] < 0].head(3)
    if not acei_examples.empty:
        print("\nExample - ACEI pairs (Tolerability Penalty):")
        for idx, row in acei_examples.iterrows():
            print(f"  {row['Drug_A_Name']} + {row['Drug_B_Name']}: "
                  f"Risk {row['Risk_Score']:.2f} → {row['CPG_Adjusted_Risk_Score']:.2f} "
                  f"({row['CPG_Tolerability_Penalty']:.2f})")

    # Example 3: No adjustment
    no_adjustment = df[(df['CPG_Outcome_Bonus'] == 0) & (df['CPG_Tolerability_Penalty'] == 0)].head(3)
    if not no_adjustment.empty:
        print("\nExample - Pairs with no CPG adjustments:")
        for idx, row in no_adjustment.iterrows():
            print(f"  {row['Drug_A_Name']} + {row['Drug_B_Name']}: "
                  f"Risk {row['Risk_Score']:.2f} → {row['CPG_Adjusted_Risk_Score']:.2f} "
                  f"(No adjustment)")

    # Save the updated dataset
    print(f"\n" + "="*80)
    print("SAVING RESULTS")
    print("="*80)
    print(f"\nSaving updated dataset to: {output_file}")
    df.to_csv(output_file, index=False)

    print(f"\nNew columns added:")
    new_columns = [
        'CPG_Outcome_Bonus',
        'CPG_Tolerability_Penalty',
        'CPG_Adjusted_Risk_Score'
    ]
    for col in new_columns:
        print(f"  - {col}")

    print("\n" + "="*80)
    print("COMPLETED SUCCESSFULLY")
    print("="*80)
    print(f"\nOriginal file backed up to: {backup_file}")
    print(f"Updated file saved to: {output_file}")
    print("\nYou can now use CPG_Adjusted_Risk_Score in your ML models!")
    print("="*80)

if __name__ == "__main__":
    main()
