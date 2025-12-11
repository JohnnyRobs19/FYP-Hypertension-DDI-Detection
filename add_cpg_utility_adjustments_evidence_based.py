#!/usr/bin/env python3
"""
Evidence-Based CPG Utility Adjustments for Drug Interaction Dataset

This script incorporates literature-justified utility adjustments based on:
1. Outcome Superiority (Cardiovascular Event Prevention)
2. Mortality/Efficacy Benefits (Survival Outcomes)
3. Tolerability/Adherence (Long-term Patient Compliance)

CRITICAL DESIGN PRINCIPLE:
These adjustments are CLINICAL PREFERENCE RULES based on published evidence,
NOT subjective drug performance ratings. Each adjustment has literature support
and aligns with Malaysian CPG principles.

Literature References:
- Roush et al. (2015): Indapamide superior to HCTZ for CV outcomes
- Alcocer et al. (2023): ACEIs reduce all-cause mortality vs ARBs
- Hu et al. (2023): ACEI cough risk 3.2x higher than ARB
- Malaysian CPG for Management of Hypertension (5th Edition)
"""

import pandas as pd
import sys
from pathlib import Path

# ==============================================================================
# EVIDENCE-BASED UTILITY ADJUSTMENTS (CORRECTED HIERARCHY)
# ==============================================================================

# TIER 1: MORTALITY/EFFICACY (HIGHEST PRIORITY - Survival Benefit)
# Evidence: Alcocer et al. (2023) - ACEIs significantly reduce all-cause mortality,
#           MI, and CV death; ARBs show non-inferiority but no significant mortality reduction
# Clinical Goal: Reduce mortality in high-risk patients
# Rationale: All-cause mortality is the ultimate "hard endpoint" in clinical medicine
EFFICACY_BONUS_ACEI = 0.05

# TIER 2: OUTCOME SUPERIORITY (High Priority - Primary CV Outcomes)
# Evidence: Roush et al. (2015) - Indapamide ~50% more potent than HCTZ
# Clinical Goal: Cardiovascular event prevention (stroke, MI, heart failure)
# Rationale: Preventing morbidity is critical but secondary to preventing mortality
OUTCOME_BONUS_INDAPAMIDE = 0.03

# TIER 3: TOLERABILITY/ADHERENCE (Lower Priority - Long-term Compliance)
# Evidence: Hu et al. (2023) - ACEI cough risk 3.2x higher than ARB
#           Malaysian CPG - ARBs have lower incidence of cough than ACEIs
# Clinical Goal: Improve long-term adherence
# Rationale: Adherence issues are important but not immediately life-threatening
TOLERABILITY_PENALTY_ACEI = -0.01

# NET EFFECT FOR ACEI CLASS:
# ACEI Total Utility = Efficacy Bonus (+0.05) + Tolerability Penalty (-0.01) = +0.04
# Interpretation: Substantial mortality benefit outweighs adherence risk for complicated hypertensive patients
#                 ACEIs are the "gold standard" for high-risk patients (survival priority)

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

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
    Calculate evidence-based CPG utility adjustments for each drug pair.

    Three-Tier Scoring Hierarchy (CORRECTED):
    1. Mortality/Efficacy (ACEI) - HIGHEST: Survival benefit (all-cause mortality)
    2. Outcome Superiority (Diuretics) - HIGH: Primary CV outcomes (events)
    3. Tolerability (ACEI) - LOWER: Adherence risk (cough)

    Args:
        df: DataFrame with drug interaction data

    Returns:
        DataFrame with added CPG adjustment columns
    """

    print("\nCalculating evidence-based utility adjustments...")
    print("="*80)

    # -------------------------------------------------------------------------
    # TIER 1: MORTALITY/EFFICACY (ACEI vs ARB) - HIGHEST PRIORITY
    # -------------------------------------------------------------------------
    print("\nTIER 1: Mortality/Efficacy Benefit (HIGHEST PRIORITY - Survival)")
    print("-" * 80)
    print(f"Adjustment: +{EFFICACY_BONUS_ACEI} for pairs containing ACEI")
    print("Evidence: Alcocer et al. (2023) - ACEIs reduce all-cause mortality,")
    print("          MI, and CV death; ARBs show non-inferiority but no")
    print("          significant mortality reduction vs placebo")
    print("Rationale: All-cause mortality is the ultimate 'hard endpoint'")

    df['CPG_Efficacy_Bonus'] = df.apply(
        lambda row: EFFICACY_BONUS_ACEI if check_class_in_pair(row, 'ACEI') else 0.0,
        axis=1
    )

    # -------------------------------------------------------------------------
    # TIER 2: OUTCOME SUPERIORITY (Diuretics) - HIGH PRIORITY
    # -------------------------------------------------------------------------
    print("\nTIER 2: Outcome Superiority (HIGH PRIORITY - CV Event Prevention)")
    print("-" * 80)
    print(f"Adjustment: +{OUTCOME_BONUS_INDAPAMIDE} for pairs containing Indapamide")
    print("Evidence: Roush et al. (2015) - Indapamide superior to HCTZ")
    print("          ~50% more potent with no added metabolic risk")
    print("Rationale: Preventing morbidity is critical but secondary to survival")

    df['CPG_Outcome_Bonus'] = df.apply(
        lambda row: OUTCOME_BONUS_INDAPAMIDE if check_drug_in_pair(row, 'Indapamide') else 0.0,
        axis=1
    )

    # -------------------------------------------------------------------------
    # TIER 3: TOLERABILITY/ADHERENCE (ACEI Cough Risk)
    # -------------------------------------------------------------------------
    print("\nTIER 3: Tolerability/Adherence (Long-term Compliance)")
    print("-" * 80)
    print(f"Adjustment: {TOLERABILITY_PENALTY_ACEI} for pairs containing ACEI")
    print("Evidence: Hu et al. (2023) - ACEI cough risk 3.2x higher than ARB")
    print("          Malaysian CPG - ARBs have lower incidence of cough")

    df['CPG_Tolerability_Penalty'] = df.apply(
        lambda row: TOLERABILITY_PENALTY_ACEI if check_class_in_pair(row, 'ACEI') else 0.0,
        axis=1
    )

    # -------------------------------------------------------------------------
    # CALCULATE TOTAL ADJUSTED RISK SCORE
    # -------------------------------------------------------------------------
    print("\nCalculating Total Adjusted Risk Score...")
    print("-" * 80)
    print("Formula: Adjusted_Score = Base_Risk_Score + Efficacy_Bonus + ")
    print("                          Outcome_Bonus + Tolerability_Penalty")
    print()
    print("For ACEI pairs:")
    print(f"  Net ACEI Adjustment = {EFFICACY_BONUS_ACEI} (mortality benefit) + {TOLERABILITY_PENALTY_ACEI} (cough risk)")
    print(f"                      = +{EFFICACY_BONUS_ACEI + TOLERABILITY_PENALTY_ACEI}")
    print("  Interpretation: SUBSTANTIAL mortality benefit outweighs adherence risk")
    print("                  ACEIs are the 'gold standard' for high-risk patients")

    df['CPG_Adjusted_Risk_Score'] = (
        df['Risk_Score'] +
        df['CPG_Outcome_Bonus'] +
        df['CPG_Efficacy_Bonus'] +
        df['CPG_Tolerability_Penalty']
    )

    return df

def main():
    """Main execution function"""

    print("="*80)
    print("EVIDENCE-BASED CPG UTILITY ADJUSTMENT SCRIPT")
    print("="*80)
    print("\nLiterature-Justified Scoring Methodology")
    print("Aligns with Malaysian CPG + International Evidence")
    print("="*80)

    # File paths
    input_file = 'FYP_Drug_Interaction_Final.csv'
    output_file = 'FYP_Drug_Interaction_Final.csv'
    backup_file = 'FYP_Drug_Interaction_Final_backup.csv'

    print(f"\nInput file: {input_file}")

    # Check if file exists
    if not Path(input_file).exists():
        print(f"Error: {input_file} not found!")
        sys.exit(1)

    # Read the dataset
    print(f"\nReading dataset...")
    df = pd.read_csv(input_file, keep_default_na=False, na_values=[''])
    print(f"Loaded {len(df)} drug pairs")

    # Remove old CPG columns if they exist
    cpg_columns = [col for col in df.columns if col.startswith('CPG_')]
    if cpg_columns:
        print(f"\nRemoving old CPG columns: {cpg_columns}")
        df = df.drop(columns=cpg_columns)

    # Backup the original file
    print(f"\nCreating backup: {backup_file}")
    df.to_csv(backup_file, index=False)

    # Calculate CPG adjustments
    df = calculate_cpg_adjustments(df)

    # Generate summary statistics
    print("\n" + "="*80)
    print("ADJUSTMENT SUMMARY (CORRECTED HIERARCHY)")
    print("="*80)

    print(f"\nTIER 1: Mortality/Efficacy (ACEI) - HIGHEST PRIORITY")
    print(f"  Bonus: +{EFFICACY_BONUS_ACEI}")
    print(f"  Pairs affected: {(df['CPG_Efficacy_Bonus'] > 0).sum()}")
    print(f"  Evidence: All-cause mortality reduction (Alcocer 2023)")

    print(f"\nTIER 2: Outcome Superiority (Indapamide) - HIGH PRIORITY")
    print(f"  Bonus: +{OUTCOME_BONUS_INDAPAMIDE}")
    print(f"  Pairs affected: {(df['CPG_Outcome_Bonus'] > 0).sum()}")
    print(f"  Evidence: CV event prevention (Roush 2015)")

    print(f"\nTIER 3: Tolerability/Adherence (ACEI) - LOWER PRIORITY")
    print(f"  Penalty: {TOLERABILITY_PENALTY_ACEI}")
    print(f"  Pairs affected: {(df['CPG_Tolerability_Penalty'] < 0).sum()}")
    print(f"  Evidence: Cough risk (Hu 2023)")

    print(f"\nNET EFFECT FOR ACEI CLASS:")
    print(f"  Total Adjustment: {EFFICACY_BONUS_ACEI} + {TOLERABILITY_PENALTY_ACEI} = {EFFICACY_BONUS_ACEI + TOLERABILITY_PENALTY_ACEI:+.2f}")
    print(f"  Interpretation: SUBSTANTIAL mortality benefit outweighs adherence risk")
    print(f"                  ACEIs are the 'gold standard' for high-risk patients")

    print("\nRISK SCORE STATISTICS")
    print(f"  Original Risk Score range: [{df['Risk_Score'].min():.2f}, {df['Risk_Score'].max():.2f}]")
    print(f"  Adjusted Risk Score range: [{df['CPG_Adjusted_Risk_Score'].min():.2f}, {df['CPG_Adjusted_Risk_Score'].max():.2f}]")
    print(f"  Mean adjustment: {(df['CPG_Adjusted_Risk_Score'] - df['Risk_Score']).mean():.4f}")

    # Show examples
    print("\n" + "="*80)
    print("EXAMPLE ADJUSTMENTS")
    print("="*80)

    # Example 1: Indapamide pair (Tier 1 only)
    indapamide_no_acei = df[(df['CPG_Outcome_Bonus'] > 0) & (df['CPG_Efficacy_Bonus'] == 0)].head(3)
    if not indapamide_no_acei.empty:
        print("\nExample 1 - Indapamide pairs (Outcome Superiority only):")
        for idx, row in indapamide_no_acei.iterrows():
            print(f"  {row['Drug_A_Name']} + {row['Drug_B_Name']}: "
                  f"Risk {row['Risk_Score']:.2f} → {row['CPG_Adjusted_Risk_Score']:.2f} "
                  f"(+{row['CPG_Outcome_Bonus']:.2f} outcome)")

    # Example 2: ACEI pair (Tier 2 + Tier 3)
    acei_no_indapamide = df[(df['CPG_Efficacy_Bonus'] > 0) & (df['CPG_Outcome_Bonus'] == 0)].head(3)
    if not acei_no_indapamide.empty:
        print("\nExample 2 - ACEI pairs (Efficacy + Tolerability):")
        for idx, row in acei_no_indapamide.iterrows():
            net_acei = row['CPG_Efficacy_Bonus'] + row['CPG_Tolerability_Penalty']
            print(f"  {row['Drug_A_Name']} + {row['Drug_B_Name']}: "
                  f"Risk {row['Risk_Score']:.2f} → {row['CPG_Adjusted_Risk_Score']:.2f} "
                  f"({net_acei:+.2f} = +{row['CPG_Efficacy_Bonus']:.2f} efficacy {row['CPG_Tolerability_Penalty']:.2f} tolerability)")

    # Example 3: ACEI + Indapamide (All tiers)
    acei_and_indapamide = df[(df['CPG_Efficacy_Bonus'] > 0) & (df['CPG_Outcome_Bonus'] > 0)].head(3)
    if not acei_and_indapamide.empty:
        print("\nExample 3 - ACEI + Indapamide pairs (All tiers):")
        for idx, row in acei_and_indapamide.iterrows():
            total_adj = (row['CPG_Outcome_Bonus'] + row['CPG_Efficacy_Bonus'] +
                        row['CPG_Tolerability_Penalty'])
            print(f"  {row['Drug_A_Name']} + {row['Drug_B_Name']}: "
                  f"Risk {row['Risk_Score']:.2f} → {row['CPG_Adjusted_Risk_Score']:.2f} "
                  f"({total_adj:+.2f} total)")

    # Example 4: No adjustment (e.g., ARB + Beta-blocker)
    no_adjustment = df[(df['CPG_Outcome_Bonus'] == 0) &
                       (df['CPG_Efficacy_Bonus'] == 0) &
                       (df['CPG_Tolerability_Penalty'] == 0)].head(3)
    if not no_adjustment.empty:
        print("\nExample 4 - Pairs with no CPG adjustments (e.g., ARB + Beta-blocker):")
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
        'CPG_Efficacy_Bonus',
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
    print("\nEvidence-Based Scoring System Applied:")
    print("  ✓ Tier 1: Outcome Superiority (Diuretics)")
    print("  ✓ Tier 2: Mortality/Efficacy (ACEI)")
    print("  ✓ Tier 3: Tolerability/Adherence (ACEI)")
    print("\nNET ACEI EFFECT: +0.02 (Mortality benefit > Adherence risk)")
    print("="*80)

if __name__ == "__main__":
    main()
