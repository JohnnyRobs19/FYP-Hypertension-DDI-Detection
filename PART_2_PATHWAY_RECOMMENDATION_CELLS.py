"""
Part 2: Knowledge-Driven Safer Medication Pathway Recommendation (XAI Framework)
Cells to add to Decision_Tree_DDI_Analysis_and_Training.ipynb,
Random_Forest_DDI_Analysis_and_Training.ipynb, and XGBoost_DDI_Analysis_and_Training.ipynb

Section 3.5.4: Knowledge-Driven Explainability (XAI) Framework
"""

# ==============================================================================
# CELL: Load XAI-Enhanced Dataset
# ==============================================================================
CELL_LOAD_XAI = """
# Load dataset with XAI Framework (Knowledge-Driven Explainability)
df_xai = pd.read_csv('FYP_Drug_Interaction_Final.csv')

print("="*80)
print("KNOWLEDGE-DRIVEN XAI FRAMEWORK DATASET LOADED")
print("Section 3.5.4: Knowledge-Driven Explainability (XAI) Framework")
print("="*80)
print(f"\\nTotal drug pairs: {len(df_xai)}")
print(f"\\nXAI columns available:")
xai_cols = [col for col in df_xai.columns if 'XAI' in col]
for col in xai_cols:
    print(f"  - {col}")

# Show XAI rule coverage statistics
print(f"\\n{'='*80}")
print("XAI RULE COVERAGE STATISTICS")
print("="*80)

rule_a_count = (df_xai['XAI_Rule_A_Mortality'] != "").sum()
rule_b_count = (df_xai['XAI_Rule_B_Tolerability'] != "").sum()
rule_c_count = (df_xai['XAI_Rule_C_CCB_RAAS_Combo'] != "").sum()
rule_d_count = (df_xai['XAI_Rule_D_Diuretic'] != "").sum()
rule_e_count = (df_xai['XAI_Rule_E_BetaBlocker'] != "").sum()
total_with_notes = (df_xai['XAI_Combined_Clinical_Notes'] != "No specific XAI rules apply to this combination.").sum()

print(f"\\nRule A (ACEI vs ARB Mortality):     {rule_a_count} pairs ({rule_a_count/len(df_xai)*100:.1f}%)")
print(f"  Evidence: Alcoer et al. (2023)")
print(f"  Focus: ACEIs reduce all-cause mortality; ARBs do not")

print(f"\\nRule B (ACEI Tolerability):         {rule_b_count} pairs ({rule_b_count/len(df_xai)*100:.1f}%)")
print(f"  Evidence: Hu et al. (2023), ACCP Guidelines (2006)")
print(f"  Focus: ACEIs have 3.2x higher cough risk vs ARBs")

print(f"\\nRule C (CCB+RAAS Combination):      {rule_c_count} pairs ({rule_c_count/len(df_xai)*100:.1f}%)")
print(f"  Evidence: Makani et al. (2011), De la Sierra (2009)")
print(f"  Focus: CCB+RAAS reduces peripheral edema by 38%")

print(f"\\nRule D (Diuretic Efficacy):         {rule_d_count} pairs ({rule_d_count/len(df_xai)*100:.1f}%)")
print(f"  Evidence: Roush et al. (2015), Mishra (2016), Burnier et al. (2019)")
print(f"  Focus: Indapamide superior to HCTZ for mortality/stroke")

print(f"\\nRule E (Beta-Blocker Phenotype):    {rule_e_count} pairs ({rule_e_count/len(df_xai)*100:.1f}%)")
print(f"  Evidence: Mahfoud et al. (2024), Mancia et al. (2022)")
print(f"  Focus: Beta-blockers target high heart rate phenotype")

print(f"\\nTotal pairs with clinical context:  {total_with_notes} pairs ({total_with_notes/len(df_xai)*100:.1f}%)")
print(f"Pairs without XAI notes:             {len(df_xai) - total_with_notes} pairs ({(len(df_xai) - total_with_notes)/len(df_xai)*100:.1f}%)")
"""

# ==============================================================================
# CELL: Severity to Risk Score Mapping
# ==============================================================================
CELL_SEVERITY_MAPPING = """
# Define severity to risk score mapping (used by model)
SEVERITY_TO_RISK = {
    'Major': 0.25,      # Highest risk
    'Moderate': 0.50,   # Medium risk
    'Minor': 0.75,      # Lower risk
    'None': 1.00        # No interaction
}

# Reverse mapping for display
RISK_TO_SEVERITY = {v: k for k, v in SEVERITY_TO_RISK.items()}

print("="*80)
print("SEVERITY-TO-RISK MAPPING")
print("="*80)
for severity, score in sorted(SEVERITY_TO_RISK.items(), key=lambda x: x[1]):
    print(f"  {severity:12s} → {score:.2f} (lower = higher risk)")
"""

# ==============================================================================
# CELL: Generate Predictions for All Pairs
# ==============================================================================
# Note: This cell is generic and works with dt_model, rf_model, or xgb_model
CELL_PREDICTIONS = """
# Generate predictions for all drug pairs using trained model
print("="*80)
print("GENERATING PREDICTIONS FOR ALL DRUG PAIRS")
print("="*80)

# Filter to pairs with Final_Severity (same as training data)
df_xai_valid = df_xai[df_xai['Final_Severity'].notna()].copy()

print(f"\\nPredicting for {len(df_xai_valid)} drug pairs...")

# Prepare features (same as training)
features_xai = ['Drug_A_Name', 'Drug_B_Name', 'Drug_A_Class', 'Drug_B_Class']
X_all = pd.get_dummies(df_xai_valid[features_xai], drop_first=False)

# Ensure same feature columns as training
missing_cols = set(X.columns) - set(X_all.columns)
for col in missing_cols:
    X_all[col] = 0
X_all = X_all[X.columns]  # Ensure same order

# Generate predictions (works with dt_model, rf_model, or xgb_model)
# Determine which model to use based on what's available
if 'dt_model' in globals() or 'dt_model' in locals():
    model_to_use = dt_model
    model_name = "Decision Tree"
elif 'rf_model' in globals() or 'rf_model' in locals():
    model_to_use = rf_model
    model_name = "Random Forest"
elif 'xgb_model' in globals() or 'xgb_model' in locals():
    model_to_use = xgb_model
    model_name = "XGBoost"
else:
    raise ValueError("No trained model found! Expected dt_model, rf_model, or xgb_model")

print(f"Using {model_name} model for predictions...")

y_pred_all = model_to_use.predict(X_all)
predicted_severities = [target_classes[i] for i in y_pred_all]

# Add predictions to dataframe
df_xai_valid['Predicted_Severity'] = predicted_severities

# Convert predictions to risk scores
df_xai_valid['Predicted_Risk_Score'] = df_xai_valid['Predicted_Severity'].map(SEVERITY_TO_RISK)

print("✓ Predictions complete!")

# Show prediction distribution
pred_dist = df_xai_valid['Predicted_Severity'].value_counts().sort_index()
print(f"\\nPredicted severity distribution:")
for sev, count in pred_dist.items():
    print(f"  {sev:12s}: {count:3d} pairs ({count/len(df_xai_valid)*100:5.1f}%)")
"""

# ==============================================================================
# CELL: Display XAI Clinical Context for Predictions
# ==============================================================================
CELL_XAI_CONTEXT = """
# Display XAI clinical context alongside predictions
print("="*80)
print("INTEGRATING XAI CLINICAL CONTEXT WITH PREDICTIONS")
print("Section 3.5.4: Knowledge-Driven Explainability Framework")
print("="*80)

print(f"\\nApproach:")
print("  1. ML Model predicts DDI severity (Major/Moderate/Minor)")
print("  2. XAI Framework provides evidence-based clinical context")
print("  3. Combined output guides safer prescribing decisions")

# Count predictions by XAI rule applicability
print(f"\\n{'='*80}")
print("PREDICTIONS WITH XAI CONTEXT")
print("="*80)

# Show examples of predictions enhanced with XAI
print(f"\\nExample 1: ACEI + CCB Combination (Rule A, B, C apply)")
acei_ccb_example = df_xai_valid[
    ((df_xai_valid['Drug_A_Class'] == 'ACEI') & (df_xai_valid['Drug_B_Class'] == 'CCB')) |
    ((df_xai_valid['Drug_A_Class'] == 'CCB') & (df_xai_valid['Drug_B_Class'] == 'ACEI'))
].head(1)

if not acei_ccb_example.empty:
    row = acei_ccb_example.iloc[0]
    print(f"  Pair: {row['Drug_A_Name']} + {row['Drug_B_Name']}")
    print(f"  Predicted Severity: {row['Predicted_Severity']} (Risk Score: {row['Predicted_Risk_Score']:.2f})")
    print(f"\\n  XAI Clinical Context:")
    if row['XAI_Rule_C_CCB_RAAS_Combo']:
        print(f"    • {row['XAI_Rule_C_CCB_RAAS_Combo'][:150]}...")

print(f"\\nExample 2: Diuretic Selection (Rule D applies)")
indapamide_example = df_xai_valid[
    (df_xai_valid['Drug_A_Name'] == 'Indapamide') | (df_xai_valid['Drug_B_Name'] == 'Indapamide')
].head(1)

if not indapamide_example.empty:
    row = indapamide_example.iloc[0]
    print(f"  Pair: {row['Drug_A_Name']} + {row['Drug_B_Name']}")
    print(f"  Predicted Severity: {row['Predicted_Severity']} (Risk Score: {row['Predicted_Risk_Score']:.2f})")
    print(f"\\n  XAI Clinical Context:")
    if row['XAI_Rule_D_Diuretic']:
        print(f"    • {row['XAI_Rule_D_Diuretic'][:150]}...")

# Statistics on XAI coverage across predictions
print(f"\\n{'='*80}")
print("XAI COVERAGE FOR PREDICTED PAIRS")
print("="*80)

severity_by_xai = df_xai_valid.groupby('Predicted_Severity').apply(
    lambda x: (x['XAI_Combined_Clinical_Notes'] != "No specific XAI rules apply to this combination.").sum()
)

print(f"\\nPairs with XAI clinical notes by predicted severity:")
for sev, count in severity_by_xai.items():
    total_sev = (df_xai_valid['Predicted_Severity'] == sev).sum()
    print(f"  {sev:12s}: {count}/{total_sev} pairs ({count/total_sev*100:.1f}% with XAI context)")
"""

# ==============================================================================
# CELL: Clinical Scenario 1 - ACEI/ARB + CCB Combinations
# ==============================================================================
CELL_SCENARIO_1 = """
# Clinical Scenario 1: Patient needs ACEI/ARB + CCB combination therapy
print("="*80)
print("CLINICAL SCENARIO 1: ACEI/ARB + CCB COMBINATION THERAPY")
print("Knowledge-Driven Recommendation (XAI Rules A, B, C)")
print("="*80)
print("\\nClinical Context:")
print("  Patient requires combination therapy:")
print("  - Either ACEI or ARB (for RAAS blockade)")
print("  - Plus CCB (for additional BP lowering)")
print("\\nQuestion: Which combination is safest AND most effective?")

# Filter to ACEI+CCB and ARB+CCB combinations
acei_ccb = df_xai_valid[
    ((df_xai_valid['Drug_A_Class'] == 'ACEI') & (df_xai_valid['Drug_B_Class'] == 'CCB')) |
    ((df_xai_valid['Drug_A_Class'] == 'CCB') & (df_xai_valid['Drug_B_Class'] == 'ACEI'))
].copy()

arb_ccb = df_xai_valid[
    ((df_xai_valid['Drug_A_Class'] == 'ARB') & (df_xai_valid['Drug_B_Class'] == 'CCB')) |
    ((df_xai_valid['Drug_A_Class'] == 'CCB') & (df_xai_valid['Drug_B_Class'] == 'ARB'))
].copy()

# Standardize drug pair names for display
def format_pair(row):
    drugs = sorted([row['Drug_A_Name'], row['Drug_B_Name']])
    return f"{drugs[0]} + {drugs[1]}"

acei_ccb['Pair'] = acei_ccb.apply(format_pair, axis=1)
arb_ccb['Pair'] = arb_ccb.apply(format_pair, axis=1)

# Rank by Predicted Risk Score (lower risk = higher score)
acei_ccb_ranked = acei_ccb.sort_values('Predicted_Risk_Score', ascending=False).head(5)
arb_ccb_ranked = arb_ccb.sort_values('Predicted_Risk_Score', ascending=False).head(5)

print(f"\\n{'='*80}")
print("TOP 5 ACEI + CCB COMBINATIONS (Ranked by ML Prediction)")
print("="*80)
print(f"{'Rank':<6} {'Combination':<35} {'Predicted':<12} {'Risk Score':<12}")
print("-" * 65)
for rank, (idx, row) in enumerate(acei_ccb_ranked.iterrows(), 1):
    print(f"{rank:<6} {row['Pair']:<35} {row['Predicted_Severity']:<12} {row['Predicted_Risk_Score']:<12.2f}")

print(f"\\n{'='*80}")
print("TOP 5 ARB + CCB COMBINATIONS (Ranked by ML Prediction)")
print("="*80)
print(f"{'Rank':<6} {'Combination':<35} {'Predicted':<12} {'Risk Score':<12}")
print("-" * 65)
for rank, (idx, row) in enumerate(arb_ccb_ranked.iterrows(), 1):
    print(f"{rank:<6} {row['Pair']:<35} {row['Predicted_Severity']:<12} {row['Predicted_Risk_Score']:<12.2f}")

# Display XAI clinical context
print(f"\\n{'='*80}")
print("XAI CLINICAL CONTEXT - WHY ACEI+CCB IS PREFERRED")
print("="*80)

# Show Rule C (CCB+RAAS combo benefit)
if not acei_ccb_ranked.empty:
    sample_acei = acei_ccb_ranked.iloc[0]
    print(f"\\n[Rule C - Combination Therapy]")
    print(f"{sample_acei['XAI_Rule_C_CCB_RAAS_Combo']}")

    print(f"\\n[Rule A - Mortality Benefit]")
    print(f"{sample_acei['XAI_Rule_A_Mortality'][:250]}...")

    print(f"\\n[Rule B - Tolerability]")
    print(f"{sample_acei['XAI_Rule_B_Tolerability'][:250]}...")

print(f"\\n{'='*80}")
print("CLINICAL RECOMMENDATION:")
print("="*80)
print(f"  ✓ BOTH combinations are effective for BP control")
print(f"  ✓ BOTH reduce CCB-induced edema by ~38% (Rule C)")
print(f"\\n  ACEI + CCB PREFERRED for high-risk patients because:")
print(f"    • ACEIs significantly reduce all-cause mortality (Rule A)")
print(f"    • Mortality benefit > tolerability concerns")
print(f"\\n  ARB + CCB alternative when:")
print(f"    • Patient has history of ACEI-induced cough")
print(f"    • Tolerability is primary concern")
print(f"\\n  Evidence: Alcocer 2023, Makani 2011, De la Sierra 2009")
"""

# ==============================================================================
# CELL: Clinical Scenario 2 - Diuretic Selection
# ==============================================================================
CELL_SCENARIO_2 = """
# Clinical Scenario 2: Choosing a diuretic (Indapamide vs HCTZ)
print("="*80)
print("CLINICAL SCENARIO 2: DIURETIC SELECTION FOR COMBINATION THERAPY")
print("Knowledge-Driven Recommendation (XAI Rule D)")
print("="*80)
print("\\nClinical Context:")
print("  Patient needs RAAS blocker + Diuretic combination")
print("\\nQuestion: Indapamide or Hydrochlorothiazide (HCTZ)?")

# Filter to RAAS + Diuretic combinations
raas_diuretic = df_xai_valid[
    (((df_xai_valid['Drug_A_Class'] == 'ACEI') | (df_xai_valid['Drug_A_Class'] == 'ARB')) &
     (df_xai_valid['Drug_B_Class'] == 'Diuretic')) |
    (((df_xai_valid['Drug_B_Class'] == 'ACEI') | (df_xai_valid['Drug_B_Class'] == 'ARB')) &
     (df_xai_valid['Drug_A_Class'] == 'Diuretic'))
].copy()

raas_diuretic['Pair'] = raas_diuretic.apply(format_pair, axis=1)

# Separate Indapamide and HCTZ pairs
indapamide_pairs = raas_diuretic[raas_diuretic['Pair'].str.contains('Indapamide')]
hctz_pairs = raas_diuretic[raas_diuretic['Pair'].str.contains('Hydrochlorothiazide')]

print(f"\\n{'='*80}")
print("RAAS BLOCKER + INDAPAMIDE COMBINATIONS")
print("="*80)
if len(indapamide_pairs) > 0:
    indapamide_ranked = indapamide_pairs.sort_values('Predicted_Risk_Score', ascending=False)
    print(f"{'Combination':<40} {'Predicted':<12} {'Risk Score':<12}")
    print("-" * 64)
    for idx, row in indapamide_ranked.iterrows():
        print(f"{row['Pair']:<40} {row['Predicted_Severity']:<12} {row['Predicted_Risk_Score']:<12.2f}")

print(f"\\n{'='*80}")
print("RAAS BLOCKER + HCTZ COMBINATIONS")
print("="*80)
if len(hctz_pairs) > 0:
    hctz_ranked = hctz_pairs.sort_values('Predicted_Risk_Score', ascending=False)
    print(f"{'Combination':<40} {'Predicted':<12} {'Risk Score':<12}")
    print("-" * 64)
    for idx, row in hctz_ranked.iterrows():
        print(f"{row['Pair']:<40} {row['Predicted_Severity']:<12} {row['Predicted_Risk_Score']:<12.2f}")

# Display XAI clinical context
print(f"\\n{'='*80}")
print("XAI CLINICAL CONTEXT - WHY INDAPAMIDE IS PREFERRED")
print("="*80)

if len(indapamide_pairs) > 0:
    sample_indap = indapamide_ranked.iloc[0]
    print(f"\\n[Rule D - Diuretic Efficacy]")
    print(f"{sample_indap['XAI_Rule_D_Diuretic']}")

if len(indapamide_pairs) > 0 and len(hctz_pairs) > 0:
    avg_indap = indapamide_ranked['Predicted_Risk_Score'].mean()
    avg_hctz = hctz_ranked['Predicted_Risk_Score'].mean()
    diff = avg_indap - avg_hctz

    print(f"\\n{'='*80}")
    print("CLINICAL RECOMMENDATION:")
    print("="*80)
    print(f"  Average Indapamide risk score: {avg_indap:.2f}")
    print(f"  Average HCTZ risk score:        {avg_hctz:.2f}")
    print(f"  Difference:                     {diff:+.2f}")
    print(f"\\n  INDAPAMIDE STRONGLY PREFERRED due to:")
    print(f"    ✓ Significantly reduces all-cause mortality, stroke, heart failure")
    print(f"    ✓ HCTZ fails to demonstrate these cardiovascular benefits")
    print(f"    ✓ ~50% more potent with superior 24-hour BP control")
    print(f"\\n  Evidence: Roush et al. 2015, Mishra 2016, Burnier et al. 2019")
"""

# ==============================================================================
# CELL: Clinical Scenario 3 - Beta-Blocker Phenotype Targeting
# ==============================================================================
CELL_SCENARIO_3 = """
# Clinical Scenario 3: Beta-Blocker for High Heart Rate Phenotype
print("="*80)
print("CLINICAL SCENARIO 3: BETA-BLOCKER PHENOTYPE TARGETING")
print("Knowledge-Driven Recommendation (XAI Rule E)")
print("="*80)
print("\\nClinical Context:")
print("  Patient has hypertension with HIGH RESTING HEART RATE (>80 bpm)")
print("\\nQuestion: Which drug class combination includes Beta-Blocker?")

# Filter to Beta-Blocker combinations
bb_combos = df_xai_valid[
    (df_xai_valid['Drug_A_Class'] == 'Beta-Blocker') |
    (df_xai_valid['Drug_B_Class'] == 'Beta-Blocker')
].copy()

bb_combos['Pair'] = bb_combos.apply(format_pair, axis=1)

# Get Beta-Blocker + RAAS combinations (most common)
bb_raas = bb_combos[
    ((bb_combos['Drug_A_Class'].isin(['ACEI', 'ARB'])) |
     (bb_combos['Drug_B_Class'].isin(['ACEI', 'ARB'])))
].copy()

print(f"\\n{'='*80}")
print("TOP BETA-BLOCKER + RAAS BLOCKER COMBINATIONS")
print("="*80)
if len(bb_raas) > 0:
    bb_raas_ranked = bb_raas.sort_values('Predicted_Risk_Score', ascending=False).head(10)
    print(f"{'Combination':<40} {'Predicted':<12} {'Risk Score':<12}")
    print("-" * 64)
    for idx, row in bb_raas_ranked.iterrows():
        print(f"{row['Pair']:<40} {row['Predicted_Severity']:<12} {row['Predicted_Risk_Score']:<12.2f}")

# Display XAI clinical context
print(f"\\n{'='*80}")
print("XAI CLINICAL CONTEXT - BETA-BLOCKER PHENOTYPE TARGETING")
print("="*80)

if len(bb_raas) > 0:
    sample_bb = bb_raas_ranked.iloc[0]
    print(f"\\n[Rule E - Beta-Blocker Phenotype]")
    print(f"{sample_bb['XAI_Rule_E_BetaBlocker']}")

print(f"\\n{'='*80}")
print("CLINICAL RECOMMENDATION:")
print("="*80)
print(f"  Beta-Blockers are APPROPRIATE for:")
print(f"    ✓ Patients with fast resting heart rate (>80 bpm)")
print(f"    ✓ Sympathetic overactivity (stress-driven hypertension)")
print(f"    ✓ Comorbidities: anxiety, migraines, arrhythmias")
print(f"\\n  NOT first-line for:")
print(f"    • Patients with normal/low heart rate")
print(f"    • Metabolic syndrome or diabetes risk")
print(f"\\n  Evidence: ESH 2023 Guidelines, Mahfoud et al. 2024, Mancia et al. 2022")
"""

# ==============================================================================
# CELL: Visualize Predictions with XAI Context
# ==============================================================================
CELL_VISUALIZATION = """
# Visualize predictions with XAI clinical context coverage
print("="*80)
print("VISUALIZING PREDICTIONS WITH XAI CLINICAL CONTEXT")
print("="*80)

# Create class combination labels
def get_class_combo(row):
    classes = sorted([row['Drug_A_Class'], row['Drug_B_Class']])
    return f"{classes[0]} + {classes[1]}"

df_xai_valid['Class_Combo'] = df_xai_valid.apply(get_class_combo, axis=1)

# Calculate average risk score by class combination
combo_scores = df_xai_valid.groupby('Class_Combo').agg({
    'Predicted_Risk_Score': ['mean', 'std', 'count']
}).reset_index()
combo_scores.columns = ['Class_Combo', 'Mean_Risk_Score', 'Std_Risk_Score', 'Count']
combo_scores = combo_scores.sort_values('Mean_Risk_Score', ascending=False)

# Calculate XAI coverage by class combination
xai_coverage = df_xai_valid.groupby('Class_Combo').apply(
    lambda x: (x['XAI_Combined_Clinical_Notes'] != "No specific XAI rules apply to this combination.").sum() / len(x) * 100
).reset_index()
xai_coverage.columns = ['Class_Combo', 'XAI_Coverage_Pct']

# Merge
combo_scores = combo_scores.merge(xai_coverage, on='Class_Combo')

# Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Bar plot of mean risk scores
colors = ['#2ecc71' if cov > 90 else '#3498db' if cov > 50 else '#95a5a6'
          for cov in combo_scores['XAI_Coverage_Pct']]

bars = ax1.barh(combo_scores['Class_Combo'], combo_scores['Mean_Risk_Score'],
                color=colors, edgecolor='black', linewidth=1.5)

for bar, (idx, row) in zip(bars, combo_scores.iterrows()):
    ax1.text(row['Mean_Risk_Score'] + 0.01, bar.get_y() + bar.get_height()/2,
             f"{row['Mean_Risk_Score']:.3f}\\n(n={int(row['Count'])})\\n{row['XAI_Coverage_Pct']:.0f}% XAI",
             va='center', fontweight='bold', fontsize=8)

ax1.set_xlabel('Average Risk Score (Higher = Safer)', fontsize=12, fontweight='bold')
ax1.set_title('Average Risk Score by Drug Class Combination\\n(Color = XAI Coverage)', fontsize=14, fontweight='bold')
ax1.grid(axis='x', alpha=0.3)
ax1.set_xlim(0, 1.1)

# XAI coverage bar plot
ax2.barh(combo_scores['Class_Combo'], combo_scores['XAI_Coverage_Pct'],
         color=colors, edgecolor='black', linewidth=1.5)

for idx, row in combo_scores.iterrows():
    ax2.text(row['XAI_Coverage_Pct'] + 2, idx,
             f"{row['XAI_Coverage_Pct']:.0f}%",
             va='center', fontweight='bold', fontsize=9)

ax2.set_xlabel('XAI Clinical Context Coverage (%)', fontsize=12, fontweight='bold')
ax2.set_title('Percentage of Pairs with XAI Clinical Notes', fontsize=14, fontweight='bold')
ax2.grid(axis='x', alpha=0.3)
ax2.set_xlim(0, 110)

plt.tight_layout()
plt.show()

print("\\n✓ Visualization complete!")
print(f"\\nColor Legend:")
print(f"  Green: >90% XAI coverage (excellent clinical context)")
print(f"  Blue: 50-90% XAI coverage (good clinical context)")
print(f"  Gray: <50% XAI coverage (limited clinical context)")
"""

# ==============================================================================
# CELL: Summary and Conclusions
# ==============================================================================
CELL_SUMMARY = """
print("="*80)
print("PART 2 SUMMARY: KNOWLEDGE-DRIVEN SAFER MEDICATION PATHWAY")
print("Section 3.5.4: Knowledge-Driven Explainability (XAI) Framework")
print("="*80)

# Determine which model was used
if 'dt_model' in globals() or 'dt_model' in locals():
    model_name = "Decision Tree"
    model_accuracy = accuracy  # from Part 1
elif 'rf_model' in globals() or 'rf_model' in locals():
    model_name = "Random Forest"
    model_accuracy = accuracy
elif 'xgb_model' in globals() or 'xgb_model' in locals():
    model_name = "XGBoost"
    model_accuracy = accuracy
else:
    model_name = "Unknown"
    model_accuracy = 0.0

summary_text = f\"\"\"
ARCHITECTURE IMPLEMENTED (Section 3.5.4):
  1. ✓ ML Prediction: {model_name} predicts DDI severity ({model_accuracy*100:.2f}% accuracy)
  2. ✓ XAI Framework: Knowledge-driven clinical context from literature
  3. ✓ Integrated Output: Predictions + Evidence-based explanations

KNOWLEDGE-DRIVEN XAI RULES IMPLEMENTED:
  • Rule A: ACEI vs ARB Mortality Benefit (Alcocer et al. 2023)
      → ACEIs reduce all-cause mortality; ARBs do not
      → Coverage: {rule_a_count} pairs ({rule_a_count/len(df_xai)*100:.1f}%)

  • Rule B: ACEI Tolerability & Adherence (Hu et al. 2023)
      → ACEIs have 3.2x higher cough risk vs ARBs
      → Coverage: {rule_b_count} pairs ({rule_b_count/len(df_xai)*100:.1f}%)

  • Rule C: CCB+RAAS Combination Therapy (Makani et al. 2011)
      → Reduces peripheral edema by 38%; improves adherence by 62%
      → Coverage: {rule_c_count} pairs ({rule_c_count/len(df_xai)*100:.1f}%)

  • Rule D: Diuretic Efficacy Optimization (Roush et al. 2015)
      → Indapamide superior to HCTZ for mortality/stroke/HF
      → Coverage: {rule_d_count} pairs ({rule_d_count/len(df_xai)*100:.1f}%)

  • Rule E: Beta-Blocker Phenotype Targeting (Mahfoud et al. 2024)
      → Indicated for high heart rate phenotype (>80 bpm)
      → Coverage: {rule_e_count} pairs ({rule_e_count/len(df_xai)*100:.1f}%)

PREDICTIONS GENERATED:
  • Total combinations analyzed: {len(df_xai_valid)}
  • Pairs with XAI clinical context: {total_with_notes} ({total_with_notes/len(df_xai)*100:.1f}%)
  • Pairs without XAI context: {len(df_xai) - total_with_notes} ({(len(df_xai) - total_with_notes)/len(df_xai)*100:.1f}%)

CLINICAL SCENARIOS ANALYZED:
  1. ✓ ACEI+CCB vs ARB+CCB combinations (Rules A, B, C)
  2. ✓ Indapamide vs HCTZ for diuretic selection (Rule D)
  3. ✓ Beta-Blocker for high heart rate phenotype (Rule E)

KEY FINDINGS:
  • ML predictions provide probabilistic severity classification
  • XAI Framework adds clinical context that ML cannot capture
  • ACEI+CCB preferred for high-risk patients (mortality benefit)
  • Indapamide superior to HCTZ (cardiovascular outcomes)
  • Beta-Blockers appropriate for sympathetic overactivity phenotype
  • System explains WHY certain combinations are preferred

ADVANTAGES OVER NUMERIC SCORING:
  • Transparent: Explicit literature citations
  • Interpretable: Clinician-readable explanations
  • Evidence-based: Grounded in peer-reviewed meta-analyses
  • Actionable: Specific recommendations with clinical rationale
  • Adaptable: Easy to add new rules as evidence emerges

NEXT STEPS:
  • Clinical validation with Dr. Nurulhuda Abdul Manaf (collaborator)
  • Align with Malaysian CPG for Hypertension (2018)
  • Integrate XAI notes into clinical decision support interface
  • Expand rules to cover additional drug classes and scenarios
\"\"\"

print(summary_text)
print("="*80)
print("✓ PART 2 COMPLETE!")
print("="*80)
"""

# ==============================================================================
# Print all cells for easy copying
# ==============================================================================
if __name__ == "__main__":
    print("="*80)
    print("PART 2: KNOWLEDGE-DRIVEN SAFER MEDICATION PATHWAY")
    print("Section 3.5.4: Knowledge-Driven Explainability (XAI) Framework")
    print("="*80)
    print("\nCopy these cells into your Jupyter notebook (Decision Tree, Random Forest, or XGBoost)")
    print("="*80)

    cells = [
        ("Load XAI-Enhanced Dataset", CELL_LOAD_XAI),
        ("Severity to Risk Score Mapping", CELL_SEVERITY_MAPPING),
        ("Generate Predictions for All Pairs", CELL_PREDICTIONS),
        ("Display XAI Clinical Context", CELL_XAI_CONTEXT),
        ("Clinical Scenario 1: ACEI/ARB + CCB", CELL_SCENARIO_1),
        ("Clinical Scenario 2: Diuretic Selection", CELL_SCENARIO_2),
        ("Clinical Scenario 3: Beta-Blocker Phenotype", CELL_SCENARIO_3),
        ("Visualization with XAI Coverage", CELL_VISUALIZATION),
        ("Summary", CELL_SUMMARY),
    ]

    for i, (title, code) in enumerate(cells, 1):
        print(f"\n{'='*80}")
        print(f"CELL {i}: {title}")
        print("="*80)
        print(code)
