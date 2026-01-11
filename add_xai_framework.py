"""
Knowledge-Driven Explainability (XAI) Framework Implementation
Adds evidence-based clinical knowledge rules to drug interaction dataset
"""

import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv('FYP_DrugBank_Inclusive.csv')

print("="*80)
print("KNOWLEDGE-DRIVEN EXPLAINABILITY (XAI) FRAMEWORK")
print("="*80)
print(f"\nOriginal dataset: {len(df)} drug pairs")
print(f"Original columns: {list(df.columns)}")

# ============================================================================
# Knowledge Rule A: Mortality Benefit Contextualization (ACEI vs. ARB)
# ============================================================================
def apply_rule_a_mortality_benefit(row):
    """
    ACE Inhibitors significantly reduce all-cause mortality, MI, and CV death.
    ARBs show no significant effect on these outcomes vs placebo.
    Source: Alcocer et al. (2023)
    """
    drug_a_class = row['Drug_A_Class']
    drug_b_class = row['Drug_B_Class']

    if drug_a_class == 'ACEI' or drug_b_class == 'ACEI':
        return ("Clinical Note: ACE Inhibitors are prioritized because meta-analyses indicate "
                "they significantly reduce the risk of all-cause mortality and cardiovascular death, "
                "whereas ARBs often show no significant effect on these specific outcomes compared "
                "to placebo (Source: Alcocer et al., 2023).")
    elif drug_a_class == 'ARB' or drug_b_class == 'ARB':
        return ("Clinical Note: ARBs have no significant effect on all-cause mortality compared "
                "to placebo. ACE Inhibitors are preferred for mortality reduction (Source: Alcocer et al., 2023).")
    return ""

# ============================================================================
# Knowledge Rule B: Tolerability & Adherence (ACEI vs. ARB Cough Risk)
# ============================================================================
def apply_rule_b_tolerability(row):
    """
    ACEIs carry 3.2-fold higher risk of dry cough vs ARBs due to bradykinin.
    ARBs have superior tolerability and are preferred when ACEI side effects occur.
    Source: Hu et al. (2023), ACCP Guidelines (2006)
    """
    drug_a_class = row['Drug_A_Class']
    drug_b_class = row['Drug_B_Class']

    if drug_a_class == 'ACEI' or drug_b_class == 'ACEI':
        return ("Clinical Note: ACE Inhibitors carry a 3.2-fold higher risk of dry cough compared "
                "to ARBs due to the accumulation of bradykinin. If tolerability becomes a barrier "
                "to adherence, ARBs are recommended as the standard alternative (Source: Hu et al., "
                "2023; ACCP Guidelines, 2006).")
    elif drug_a_class == 'ARB' or drug_b_class == 'ARB':
        return ("Clinical Note: ARBs have a superior tolerability profile with significantly lower "
                "risk of dry cough compared to ACE Inhibitors (3.2-fold lower risk). ARBs are the "
                "preferred alternative when cough or other ACEI-related side effects limit adherence "
                "(Source: Hu et al., 2023; ACCP Guidelines, 2006).")
    return ""

# ============================================================================
# Knowledge Rule C: Combination Therapy Strategy (ACEI/ARB + CCB)
# ============================================================================
def apply_rule_c_ccb_raas_combo(row):
    """
    RAAS blocker + CCB combination reduces peripheral edema by 38%.
    ACEIs slightly better than ARBs (2.7% vs 3.7% edema rate).
    Source: Makani et al. (2011), De la Sierra (2009)
    """
    drug_a_class = row['Drug_A_Class']
    drug_b_class = row['Drug_B_Class']

    # Check if combination contains CCB + (ACEI or ARB)
    classes = {drug_a_class, drug_b_class}

    if 'CCB' in classes and ('ACEI' in classes or 'ARB' in classes):
        if 'ACEI' in classes:
            return ("Clinical Note: This Combination Therapy is RECOMMENDED. Calcium Channel Blockers "
                    "(CCBs) can cause leg swelling by widening arteries more than veins. The added "
                    "ACE Inhibitor helps widen the veins, balancing the pressure and reducing swelling "
                    "risk by ~38%. ACEIs are superior to ARBs for edema prevention (2.7% vs 3.7% rate). "
                    "(Sources: Makani et al., 2011; De la Sierra, 2009).")
        else:  # ARB
            return ("Clinical Note: This Combination Therapy is recommended. Calcium Channel Blockers "
                    "(CCBs) can cause leg swelling by widening arteries more than veins. The added "
                    "ARB helps widen the veins, balancing the pressure and reducing swelling risk by "
                    "~38%. Note: ACEIs are slightly more effective than ARBs for edema prevention. "
                    "(Sources: Makani et al., 2011; De la Sierra, 2009).")
    return ""

# ============================================================================
# Knowledge Rule D: Diuretic Efficacy Optimization (Indapamide vs. HCTZ)
# ============================================================================
def apply_rule_d_diuretic_preference(row):
    """
    Indapamide significantly reduces mortality/stroke/HF; HCTZ does not.
    Indapamide is ~50% more potent with superior 24h BP control.
    Source: Roush et al. (2015), Mishra (2016), Burnier et al. (2019)
    """
    drug_a_name = row['Drug_A_Name']
    drug_b_name = row['Drug_B_Name']

    has_indapamide = 'Indapamide' in [drug_a_name, drug_b_name]
    has_hctz = 'Hydrochlorothiazide' in [drug_a_name, drug_b_name]

    if has_indapamide:
        return ("Clinical Note: Indapamide is prioritized over Hydrochlorothiazide (HCTZ) because "
                "meta-analyses demonstrate it significantly reduces all-cause mortality, stroke, and "
                "heart failure, whereas HCTZ fails to consistently show these benefits and offers "
                "inferior 24-hour blood pressure control (Source: Roush et al., 2015; Mishra, 2016; "
                "Burnier et al., 2019).")
    elif has_hctz:
        return ("Clinical Note: Hydrochlorothiazide (HCTZ) has inferior cardiovascular protection "
                "compared to Indapamide. Meta-analyses show HCTZ fails to significantly reduce "
                "mortality, stroke, or heart failure. Consider switching to Indapamide for superior "
                "outcomes (Source: Roush et al., 2015; Mishra, 2016; Burnier et al., 2019).")
    return ""

# ============================================================================
# Knowledge Rule E: Beta-Blocker Phenotype Targeting (High Heart Rate)
# ============================================================================
def apply_rule_e_beta_blocker_phenotype(row):
    """
    Beta-blockers are indicated for patients with high resting HR (>80 bpm).
    They target sympathetic overactivity and manage comorbidities.
    Source: Mahfoud et al. (2024), Mancia et al. (2022)
    """
    drug_a_class = row['Drug_A_Class']
    drug_b_class = row['Drug_B_Class']

    if drug_a_class == 'Beta-Blocker' or drug_b_class == 'Beta-Blocker':
        return ("Clinical Note: Beta-blockers are one of the five major antihypertensive classes, "
                "specifically indicated for patients with a fast resting heart rate (>80 bpm) to "
                "target sympathetic overactivity (stress signals). They are also preferred for "
                "managing comorbidities like anxiety or arrhythmias (Source: Mahfoud et al., 2024; "
                "Mancia et al., 2022).")
    return ""

# ============================================================================
# Apply all XAI rules
# ============================================================================
print("\n📋 Applying Knowledge-Driven XAI Rules...")

df['XAI_Rule_A_Mortality'] = df.apply(apply_rule_a_mortality_benefit, axis=1)
df['XAI_Rule_B_Tolerability'] = df.apply(apply_rule_b_tolerability, axis=1)
df['XAI_Rule_C_CCB_RAAS_Combo'] = df.apply(apply_rule_c_ccb_raas_combo, axis=1)
df['XAI_Rule_D_Diuretic'] = df.apply(apply_rule_d_diuretic_preference, axis=1)
df['XAI_Rule_E_BetaBlocker'] = df.apply(apply_rule_e_beta_blocker_phenotype, axis=1)

print("✓ Rule A (ACEI Mortality Benefit) applied")
print("✓ Rule B (ACEI vs ARB Tolerability) applied")
print("✓ Rule C (CCB+RAAS Combination) applied")
print("✓ Rule D (Diuretic Preference) applied")
print("✓ Rule E (Beta-Blocker Phenotype) applied")

# ============================================================================
# Create combined XAI clinical notes
# ============================================================================
def combine_xai_notes(row):
    """Combine all applicable XAI rules into a single clinical advisory."""
    notes = []

    if row['XAI_Rule_A_Mortality']:
        notes.append("[RULE A - Mortality] " + row['XAI_Rule_A_Mortality'])
    if row['XAI_Rule_B_Tolerability']:
        notes.append("[RULE B - Tolerability] " + row['XAI_Rule_B_Tolerability'])
    if row['XAI_Rule_C_CCB_RAAS_Combo']:
        notes.append("[RULE C - Combination Therapy] " + row['XAI_Rule_C_CCB_RAAS_Combo'])
    if row['XAI_Rule_D_Diuretic']:
        notes.append("[RULE D - Diuretic Efficacy] " + row['XAI_Rule_D_Diuretic'])
    if row['XAI_Rule_E_BetaBlocker']:
        notes.append("[RULE E - Beta-Blocker Phenotype] " + row['XAI_Rule_E_BetaBlocker'])

    return "\n\n".join(notes) if notes else "No specific XAI rules apply to this combination."

df['XAI_Combined_Clinical_Notes'] = df.apply(combine_xai_notes, axis=1)
print("✓ Combined clinical notes generated")

# ============================================================================
# Statistics and validation
# ============================================================================
print("\n" + "="*80)
print("XAI FRAMEWORK STATISTICS")
print("="*80)

rule_a_count = (df['XAI_Rule_A_Mortality'] != "").sum()
rule_b_count = (df['XAI_Rule_B_Tolerability'] != "").sum()
rule_c_count = (df['XAI_Rule_C_CCB_RAAS_Combo'] != "").sum()
rule_d_count = (df['XAI_Rule_D_Diuretic'] != "").sum()
rule_e_count = (df['XAI_Rule_E_BetaBlocker'] != "").sum()

print(f"\nRule A (ACEI Mortality):      {rule_a_count} pairs ({rule_a_count/len(df)*100:.1f}%)")
print(f"Rule B (ACEI/ARB Tolerability): {rule_b_count} pairs ({rule_b_count/len(df)*100:.1f}%)")
print(f"Rule C (CCB+RAAS Combo):      {rule_c_count} pairs ({rule_c_count/len(df)*100:.1f}%)")
print(f"Rule D (Diuretic):            {rule_d_count} pairs ({rule_d_count/len(df)*100:.1f}%)")
print(f"Rule E (Beta-Blocker):        {rule_e_count} pairs ({rule_e_count/len(df)*100:.1f}%)")

total_with_notes = (df['XAI_Combined_Clinical_Notes'] != "No specific XAI rules apply to this combination.").sum()
print(f"\nTotal pairs with XAI notes: {total_with_notes} ({total_with_notes/len(df)*100:.1f}%)")
print(f"Pairs without XAI notes:    {len(df) - total_with_notes} ({(len(df) - total_with_notes)/len(df)*100:.1f}%)")

# ============================================================================
# Save updated dataset
# ============================================================================
print("\n" + "="*80)
print("SAVING UPDATED DATASET")
print("="*80)

output_file = 'FYP_DrugBank_Inclusive.csv'
df.to_csv(output_file, index=False)

print(f"\n✓ Dataset saved to: {output_file}")
print(f"  Total rows: {len(df)}")
print(f"  Total columns: {len(df.columns)}")
print(f"\nNew XAI columns added:")
print("  1. XAI_Rule_A_Mortality")
print("  2. XAI_Rule_B_Tolerability")
print("  3. XAI_Rule_C_CCB_RAAS_Combo")
print("  4. XAI_Rule_D_Diuretic")
print("  5. XAI_Rule_E_BetaBlocker")
print("  6. XAI_Combined_Clinical_Notes")

# ============================================================================
# Display sample XAI notes
# ============================================================================
print("\n" + "="*80)
print("SAMPLE XAI CLINICAL NOTES")
print("="*80)

# Show examples of each rule
print("\n[Example - Rule A: ACEI Mortality]")
sample_a = df[df['XAI_Rule_A_Mortality'] != ""].head(1)
if not sample_a.empty:
    print(f"Pair: {sample_a.iloc[0]['Drug_A_Name']} + {sample_a.iloc[0]['Drug_B_Name']}")
    print(f"Note: {sample_a.iloc[0]['XAI_Rule_A_Mortality'][:150]}...")

print("\n[Example - Rule C: CCB+RAAS Combination]")
sample_c = df[df['XAI_Rule_C_CCB_RAAS_Combo'] != ""].head(1)
if not sample_c.empty:
    print(f"Pair: {sample_c.iloc[0]['Drug_A_Name']} + {sample_c.iloc[0]['Drug_B_Name']}")
    print(f"Note: {sample_c.iloc[0]['XAI_Rule_C_CCB_RAAS_Combo'][:150]}...")

print("\n[Example - Rule D: Diuretic Preference]")
sample_d = df[df['XAI_Rule_D_Diuretic'] != ""].head(1)
if not sample_d.empty:
    print(f"Pair: {sample_d.iloc[0]['Drug_A_Name']} + {sample_d.iloc[0]['Drug_B_Name']}")
    print(f"Note: {sample_d.iloc[0]['XAI_Rule_D_Diuretic'][:150]}...")

print("\n" + "="*80)
print("XAI FRAMEWORK IMPLEMENTATION COMPLETE")
print("="*80)
