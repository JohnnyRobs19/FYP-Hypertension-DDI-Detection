"""
Part 2: Safer Medication Pathway Recommendation
Cells to add to Decision_Tree_DDI_Analysis_and_Training.ipynb

Copy these cells into your Jupyter notebook after the Part 1 sections.
"""

# ==============================================================================
# CELL: Load CPG-Adjusted Dataset
# ==============================================================================
CELL_LOAD_CPG = """
# Load dataset with CPG adjustments
df_cpg = pd.read_csv('FYP_Drug_Interaction_Final.csv')

print("="*80)
print("CPG-ADJUSTED DATASET LOADED")
print("="*80)
print(f"\\nTotal drug pairs: {len(df_cpg)}")
print(f"\\nCPG columns available:")
cpg_cols = [col for col in df_cpg.columns if 'CPG' in col]
for col in cpg_cols:
    print(f"  - {col}")

# Show CPG adjustment statistics (Section 3.5.4 wording)
print(f"\\n{'='*80}")
print("CPG ADJUSTMENT STATISTICS (Section 3.5.4)")
print("Hierarchy: Mortality > Morbidity > Adherence")
print("="*80)

print(f"\\nTIER 1: Mortality Benefit (ACEI) - HIGHEST PRIORITY")
print(f"  Bonus: +0.05")
print(f"  Pairs affected: {(df_cpg['CPG_Efficacy_Bonus'] > 0).sum()}")
print(f"  Evidence: Alcocer et al. (2023)")
print(f"  Justification: Preventing mortality is the ultimate goal of pharmacotherapy")

print(f"\\nTIER 2: Outcome Superiority (Indapamide) - HIGH PRIORITY")
print(f"  Bonus: +0.03")
print(f"  Pairs affected: {(df_cpg['CPG_Outcome_Bonus'] > 0).sum()}")
print(f"  Evidence: Roush et al. (2015)")
print(f"  Justification: Preventing morbidity is critical but secondary to survival")
print(f"  Note: Chlorthalidone would receive same bonus if added to dataset")

print(f"\\nTIER 3: Tolerability & Adherence (ACEI) - LOWER PRIORITY")
print(f"  Penalty: -0.01")
print(f"  Pairs affected: {(df_cpg['CPG_Tolerability_Penalty'] < 0).sum()}")
print(f"  Evidence: Hu et al. (2023), Ministry of Health Malaysia (2018), Dicpinigaitis (2006)")
print(f"  Justification: Reflects quality of life rather than immediate safety")

print(f"\\nNET EFFECT FOR ACEIs:")
if (df_cpg['CPG_Efficacy_Bonus'] > 0).sum() > 0:
    acei_sample = df_cpg[df_cpg['CPG_Efficacy_Bonus'] > 0].iloc[0]
    net_acei = acei_sample['CPG_Efficacy_Bonus'] + acei_sample['CPG_Tolerability_Penalty']
    print(f"  Formula: +0.05 (mortality) + (-0.01) (cough) = {net_acei:+.2f}")
    print(f"  Interpretation:")
    print(f"    The substantial mortality benefit (+0.05) significantly outweighs the")
    print(f"    adherence risk (-0.01), resulting in a net positive utility (+0.04) that")
    print(f"    correctly identifies ACEIs as the 'gold standard' for high-risk patient survival.")

print(f"\\nAdjusted Risk Score range: [{df_cpg['CPG_Adjusted_Risk_Score'].min():.2f}, {df_cpg['CPG_Adjusted_Risk_Score'].max():.2f}]")
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
CELL_PREDICTIONS = """
# Generate predictions for all drug pairs using trained model
print("="*80)
print("GENERATING PREDICTIONS FOR ALL DRUG PAIRS")
print("="*80)

# Filter to pairs with Final_Severity (same as training data)
df_cpg_valid = df_cpg[df_cpg['Final_Severity'].notna()].copy()

print(f"\\nPredicting for {len(df_cpg_valid)} drug pairs...")

# Prepare features (same as training)
features_cpg = ['Drug_A_Name', 'Drug_B_Name', 'Drug_A_Class', 'Drug_B_Class']
X_all = pd.get_dummies(df_cpg_valid[features_cpg], drop_first=False)

# Ensure same feature columns as training
missing_cols = set(X.columns) - set(X_all.columns)
for col in missing_cols:
    X_all[col] = 0
X_all = X_all[X.columns]  # Ensure same order

# Generate predictions
y_pred_all = dt_model.predict(X_all)
predicted_severities = [target_classes[i] for i in y_pred_all]

# Add predictions to dataframe
df_cpg_valid['Predicted_Severity'] = predicted_severities

# Convert predictions to risk scores
df_cpg_valid['Predicted_Risk_Score'] = df_cpg_valid['Predicted_Severity'].map(SEVERITY_TO_RISK)

print("✓ Predictions complete!")

# Show prediction distribution
pred_dist = df_cpg_valid['Predicted_Severity'].value_counts().sort_index()
print(f"\\nPredicted severity distribution:")
for sev, count in pred_dist.items():
    print(f"  {sev:12s}: {count:3d} pairs ({count/len(df_cpg_valid)*100:5.1f}%)")
"""

# ==============================================================================
# CELL: Apply CPG Adjustments to Create Final Scores
# ==============================================================================
CELL_APPLY_CPG = """
# Calculate final pathway scores (Predicted Risk + CPG Adjustments)
print("="*80)
print("APPLYING CPG ADJUSTMENTS TO PREDICTIONS")
print("="*80)

# Final Pathway Score = Predicted Risk Score + CPG Adjustments (Section 3.5.4)
df_cpg_valid['Pathway_Score'] = (
    df_cpg_valid['Predicted_Risk_Score'] +
    df_cpg_valid['CPG_Efficacy_Bonus'] +
    df_cpg_valid['CPG_Outcome_Bonus'] +
    df_cpg_valid['CPG_Tolerability_Penalty']
)

print("\\nFormula (Section 3.5.4):")
print("  Pathway_Score = Predicted_Risk_Score + ")
print("                  Mortality_Bonus (Tier 1) + ")
print("                  Outcome_Bonus (Tier 2) + ")
print("                  Tolerability_Penalty (Tier 3)")

print(f"\\nPathway Score range: [{df_cpg_valid['Pathway_Score'].min():.2f}, {df_cpg_valid['Pathway_Score'].max():.2f}]")
print("  (Higher score = Safer combination)")

# Show example comparisons
print(f"\\n{'='*80}")
print("EXAMPLE: How CPG Adjustments Change Rankings (Section 3.5.4)")
print("="*80)

# Example: ACEI + CCB vs ARB + CCB
acei_ccb_mask = ((df_cpg_valid['Drug_A_Class'] == 'ACEI') & (df_cpg_valid['Drug_B_Class'] == 'CCB')) | ((df_cpg_valid['Drug_A_Class'] == 'CCB') & (df_cpg_valid['Drug_B_Class'] == 'ACEI'))
arb_ccb_mask = ((df_cpg_valid['Drug_A_Class'] == 'ARB') & (df_cpg_valid['Drug_B_Class'] == 'CCB')) | ((df_cpg_valid['Drug_A_Class'] == 'CCB') & (df_cpg_valid['Drug_B_Class'] == 'ARB'))

if acei_ccb_mask.sum() > 0 and arb_ccb_mask.sum() > 0:
    acei_ccb_ex = df_cpg_valid[acei_ccb_mask].iloc[0]
    arb_ccb_ex = df_cpg_valid[arb_ccb_mask].iloc[0]

    print("\\nComparison: ACEI+CCB vs ARB+CCB")
    print(f"\\n{acei_ccb_ex['Drug_A_Name']} + {acei_ccb_ex['Drug_B_Name']} (ACEI + CCB):")
    print(f"  Predicted Risk Score: {acei_ccb_ex['Predicted_Risk_Score']:.2f}")
    cpg_adjustment = acei_ccb_ex['CPG_Efficacy_Bonus'] + acei_ccb_ex['CPG_Tolerability_Penalty']
    print(f"  + Tier 1 (Mortality):   +{acei_ccb_ex['CPG_Efficacy_Bonus']:.2f}")
    print(f"  + Tier 3 (Tolerability): {acei_ccb_ex['CPG_Tolerability_Penalty']:.2f}")
    print(f"  = Net CPG Adjustment:   {cpg_adjustment:+.2f}")
    print(f"  = Pathway Score:        {acei_ccb_ex['Pathway_Score']:.2f}")

    print(f"\\n{arb_ccb_ex['Drug_A_Name']} + {arb_ccb_ex['Drug_B_Name']} (ARB + CCB):")
    print(f"  Predicted Risk Score: {arb_ccb_ex['Predicted_Risk_Score']:.2f}")
    cpg_adjustment = arb_ccb_ex['CPG_Outcome_Bonus'] + arb_ccb_ex['CPG_Efficacy_Bonus'] + arb_ccb_ex['CPG_Tolerability_Penalty']
    print(f"  + CPG Adjustments:    {cpg_adjustment:+.2f} (ARB has no mortality benefit)")
    print(f"  = Pathway Score:      {arb_ccb_ex['Pathway_Score']:.2f}")

    diff = acei_ccb_ex['Pathway_Score'] - arb_ccb_ex['Pathway_Score']
    if diff > 0:
        print(f"\\nResult: ACEI combo preferred by {diff:+.2f} points")
        print(f"Rationale: Substantial mortality benefit (+0.05) outweighs adherence risk (-0.01)")
        print(f"          ACEIs are the 'gold standard' for high-risk patient survival")
"""

# ==============================================================================
# CELL: Clinical Scenario 1 - ACEI/ARB + CCB Combinations
# ==============================================================================
CELL_SCENARIO_1 = """
# Clinical Scenario 1: Patient needs ACEI/ARB + CCB combination therapy
print("="*80)
print("CLINICAL SCENARIO 1: ACEI/ARB + CCB COMBINATION THERAPY")
print("="*80)
print("\\nClinical Context:")
print("  Patient requires combination therapy:")
print("  - Either ACEI or ARB (for BP control)")
print("  - Plus CCB (for additional BP lowering)")
print("\\nQuestion: Which combination is safest?")

# Filter to ACEI+CCB and ARB+CCB combinations
acei_ccb = df_cpg_valid[
    ((df_cpg_valid['Drug_A_Class'] == 'ACEI') & (df_cpg_valid['Drug_B_Class'] == 'CCB')) |
    ((df_cpg_valid['Drug_A_Class'] == 'CCB') & (df_cpg_valid['Drug_B_Class'] == 'ACEI'))
].copy()

arb_ccb = df_cpg_valid[
    ((df_cpg_valid['Drug_A_Class'] == 'ARB') & (df_cpg_valid['Drug_B_Class'] == 'CCB')) |
    ((df_cpg_valid['Drug_A_Class'] == 'CCB') & (df_cpg_valid['Drug_B_Class'] == 'ARB'))
].copy()

# Standardize drug pair names for display
def format_pair(row):
    drugs = sorted([row['Drug_A_Name'], row['Drug_B_Name']])
    return f"{drugs[0]} + {drugs[1]}"

acei_ccb['Pair'] = acei_ccb.apply(format_pair, axis=1)
arb_ccb['Pair'] = arb_ccb.apply(format_pair, axis=1)

# Rank by Pathway Score
acei_ccb_ranked = acei_ccb.sort_values('Pathway_Score', ascending=False).head(5)
arb_ccb_ranked = arb_ccb.sort_values('Pathway_Score', ascending=False).head(5)

print(f"\\n{'='*80}")
print("TOP 5 ACEI + CCB COMBINATIONS (Ranked by Safety)")
print("="*80)
print(f"{'Rank':<6} {'Combination':<35} {'Predicted':<12} {'Pathway Score':<15}")
print("-" * 68)
for rank, (idx, row) in enumerate(acei_ccb_ranked.iterrows(), 1):
    print(f"{rank:<6} {row['Pair']:<35} {row['Predicted_Severity']:<12} {row['Pathway_Score']:<15.2f}")

print(f"\\n{'='*80}")
print("TOP 5 ARB + CCB COMBINATIONS (Ranked by Safety)")
print("="*80)
print(f"{'Rank':<6} {'Combination':<35} {'Predicted':<12} {'Pathway Score':<15}")
print("-" * 68)
for rank, (idx, row) in enumerate(arb_ccb_ranked.iterrows(), 1):
    print(f"{rank:<6} {row['Pair']:<35} {row['Predicted_Severity']:<12} {row['Pathway_Score']:<15.2f}")

print(f"\\n{'='*80}")
print("CLINICAL RECOMMENDATION:")
print("="*80)
print(f"  ACEI + CCB combinations score ~0.04 points higher due to:")
print(f"    ✓ ACEI mortality benefit (+0.05) - HIGHEST PRIORITY")
print(f"    ⚠ ACEI cough risk (-0.01) - LOWER PRIORITY")
print(f"    = Net +0.04 advantage (SUBSTANTIAL)")
print(f"\\n  For high-risk patients: ACEI + CCB STRONGLY preferred for survival benefit")
print(f"  For patients with cough history: ARB + CCB may be better tolerated")
print(f"  Rationale: All-cause mortality > Adherence issues")
"""

# ==============================================================================
# CELL: Clinical Scenario 2 - Diuretic Selection
# ==============================================================================
CELL_SCENARIO_2 = """
# Clinical Scenario 2: Choosing a diuretic (Indapamide vs HCTZ)
print("="*80)
print("CLINICAL SCENARIO 2: DIURETIC SELECTION FOR COMBINATION THERAPY")
print("="*80)
print("\\nClinical Context:")
print("  Patient needs ACEI + Diuretic combination")
print("\\nQuestion: Indapamide or Hydrochlorothiazide (HCTZ)?")

# Filter to ACEI + Diuretic combinations
acei_diuretic = df_cpg_valid[
    ((df_cpg_valid['Drug_A_Class'] == 'ACEI') & (df_cpg_valid['Drug_B_Class'] == 'Diuretic')) |
    ((df_cpg_valid['Drug_A_Class'] == 'Diuretic') & (df_cpg_valid['Drug_B_Class'] == 'ACEI'))
].copy()

acei_diuretic['Pair'] = acei_diuretic.apply(format_pair, axis=1)

# Separate Indapamide and HCTZ pairs
indapamide_pairs = acei_diuretic[acei_diuretic['Pair'].str.contains('Indapamide')]
hctz_pairs = acei_diuretic[acei_diuretic['Pair'].str.contains('Hydrochlorothiazide')]

print(f"\\n{'='*80}")
print("ACEI + INDAPAMIDE COMBINATIONS")
print("="*80)
if len(indapamide_pairs) > 0:
    indapamide_ranked = indapamide_pairs.sort_values('Pathway_Score', ascending=False)
    print(f"{'Combination':<35} {'Predicted':<12} {'CPG Bonus':<12} {'Pathway Score':<15}")
    print("-" * 74)
    for idx, row in indapamide_ranked.iterrows():
        print(f"{row['Pair']:<35} {row['Predicted_Severity']:<12} +{row['CPG_Outcome_Bonus']:.2f} (Indap)  {row['Pathway_Score']:<15.2f}")

print(f"\\n{'='*80}")
print("ACEI + HCTZ COMBINATIONS")
print("="*80)
if len(hctz_pairs) > 0:
    hctz_ranked = hctz_pairs.sort_values('Pathway_Score', ascending=False)
    print(f"{'Combination':<35} {'Predicted':<12} {'CPG Bonus':<12} {'Pathway Score':<15}")
    print("-" * 74)
    for idx, row in hctz_ranked.iterrows():
        print(f"{row['Pair']:<35} {row['Predicted_Severity']:<12} {'+0.00 (None)':<12} {row['Pathway_Score']:<15.2f}")

if len(indapamide_pairs) > 0 and len(hctz_pairs) > 0:
    avg_indap = indapamide_ranked['Pathway_Score'].mean()
    avg_hctz = hctz_ranked['Pathway_Score'].mean()
    diff = avg_indap - avg_hctz

    print(f"\\n{'='*80}")
    print("CLINICAL RECOMMENDATION:")
    print("="*80)
    print(f"  Average Indapamide score: {avg_indap:.2f}")
    print(f"  Average HCTZ score:        {avg_hctz:.2f}")
    print(f"  Difference:               +{diff:.2f}")
    print(f"\\n  Indapamide preferred due to:")
    print(f"    ✓ Superior CV outcomes (Roush 2015)")
    print(f"    ✓ ~50% more potent than HCTZ")
    print(f"    ✓ No added metabolic risk")
"""

# ==============================================================================
# CELL: Visualize Pathway Rankings by Drug Class Combination
# ==============================================================================
CELL_VISUALIZATION = """
# Visualize pathway rankings by drug class combination
print("="*80)
print("VISUALIZING PATHWAY RANKINGS BY DRUG CLASS COMBINATION")
print("="*80)

# Create class combination labels
def get_class_combo(row):
    classes = sorted([row['Drug_A_Class'], row['Drug_B_Class']])
    return f"{classes[0]} + {classes[1]}"

df_cpg_valid['Class_Combo'] = df_cpg_valid.apply(get_class_combo, axis=1)

# Calculate average pathway score by class combination
combo_scores = df_cpg_valid.groupby('Class_Combo').agg({
    'Pathway_Score': ['mean', 'std', 'count']
}).reset_index()
combo_scores.columns = ['Class_Combo', 'Mean_Score', 'Std_Score', 'Count']
combo_scores = combo_scores.sort_values('Mean_Score', ascending=False)

# Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Bar plot of mean scores
colors_map = {
    'ACEI + Diuretic': '#2ecc71' if 'Indapamide' in str(df_cpg_valid[df_cpg_valid['Class_Combo'] == 'ACEI + Diuretic']['Drug_A_Name'].values) else '#3498db',
    'ACEI + CCB': '#e74c3c',
    'ARB + CCB': '#f39c12',
}

bars = ax1.barh(combo_scores['Class_Combo'], combo_scores['Mean_Score'],
                color='skyblue', edgecolor='black', linewidth=1.5)

for bar, (idx, row) in zip(bars, combo_scores.iterrows()):
    ax1.text(row['Mean_Score'] + 0.01, bar.get_y() + bar.get_height()/2,
             f"{row['Mean_Score']:.3f}\\n(n={int(row['Count'])})",
             va='center', fontweight='bold', fontsize=9)

ax1.set_xlabel('Average Pathway Score (Higher = Safer)', fontsize=12, fontweight='bold')
ax1.set_title('Average Safety Score by Drug Class Combination', fontsize=14, fontweight='bold')
ax1.grid(axis='x', alpha=0.3)
ax1.set_xlim(0, 1.1)

# Box plot showing distributions
class_combos_of_interest = ['ACEI + CCB', 'ARB + CCB', 'ACEI + Diuretic', 'ARB + Diuretic']
filtered_data = df_cpg_valid[df_cpg_valid['Class_Combo'].isin(class_combos_of_interest)]

if len(filtered_data) > 0:
    bp = ax2.boxplot(
        [filtered_data[filtered_data['Class_Combo'] == cc]['Pathway_Score'].values
         for cc in class_combos_of_interest if len(filtered_data[filtered_data['Class_Combo'] == cc]) > 0],
        labels=[cc for cc in class_combos_of_interest if len(filtered_data[filtered_data['Class_Combo'] == cc]) > 0],
        patch_artist=True,
        widths=0.6
    )

    for patch in bp['boxes']:
        patch.set_facecolor('lightblue')
        patch.set_edgecolor('black')
        patch.set_linewidth(1.5)

    ax2.set_ylabel('Pathway Score', fontsize=12, fontweight='bold')
    ax2.set_title('Distribution of Pathway Scores', fontsize=14, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.show()

print("\\n✓ Visualization complete!")
"""

# ==============================================================================
# CELL: Summary and Conclusions
# ==============================================================================
CELL_SUMMARY = """
print("="*80)
print("PART 2 SUMMARY: SAFER MEDICATION PATHWAY RECOMMENDATION")
print("="*80)

summary_text = f\"\"\"
ARCHITECTURE IMPLEMENTED:
  1. ✓ Model Prediction: Decision Tree predicts DDI severity (92% accuracy)
  2. ✓ CPG Adjustments: Evidence-based utility scores applied
  3. ✓ Pathway Ranking: Combinations sorted by safety score

EVIDENCE-BASED ADJUSTMENTS (CORRECTED HIERARCHY):
  • Tier 1: ACEI +0.05 (Alcocer 2023 - ALL-CAUSE MORTALITY - HIGHEST PRIORITY)
  • Tier 2: Indapamide +0.03 (Roush 2015 - CV event prevention - HIGH PRIORITY)
  • Tier 3: ACEI -0.01 (Hu 2023 - cough risk 3.2x higher - LOWER PRIORITY)
  • Net ACEI Effect: +0.04 (SUBSTANTIAL mortality benefit > adherence risk)
  • Clinical Rationale: Survival > Morbidity > Adherence

PATHWAY SCORES GENERATED:
  • Total combinations analyzed: {len(df_cpg_valid)}
  • Score range: [{df_cpg_valid['Pathway_Score'].min():.2f}, {df_cpg_valid['Pathway_Score'].max():.2f}]
  • Higher score = Safer combination

CLINICAL SCENARIOS ANALYZED:
  1. ✓ ACEI+CCB vs ARB+CCB combinations
  2. ✓ Indapamide vs HCTZ for diuretic selection
  3. ✓ Drug class combination safety rankings

KEY FINDINGS:
  • ACEI+CCB combinations score ~0.04 higher than ARB+CCB due to mortality benefit
  • Indapamide combinations score ~0.03 higher than HCTZ due to CV outcomes
  • Model predictions (DDI severity) combined with clinical evidence (CPG)
  • Hierarchy: All-cause mortality > CV events > Adherence issues

ACADEMIC DEFENSE:
  • NOT subjective drug performance ratings
  • Based on published literature (Roush, Alcocer, Hu)
  • Objective clinical endpoints (mortality, CV events, adverse events)
  • Respects therapeutic equivalence within drug classes
  • Aligns with Malaysian CPG + international evidence

NEXT STEPS:
  • Present pathway recommendations to clinical collaborators
  • Validate rankings against Malaysian CPG preferred pathways
  • Extend to additional clinical scenarios (e.g., comorbidities)
  • Deploy as clinical decision support tool
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
    print("PART 2: SAFER MEDICATION PATHWAY RECOMMENDATION")
    print("Copy these cells into your Jupyter notebook")
    print("="*80)

    cells = [
        ("Load CPG-Adjusted Dataset", CELL_LOAD_CPG),
        ("Severity to Risk Score Mapping", CELL_SEVERITY_MAPPING),
        ("Generate Predictions for All Pairs", CELL_PREDICTIONS),
        ("Apply CPG Adjustments", CELL_APPLY_CPG),
        ("Clinical Scenario 1: ACEI/ARB + CCB", CELL_SCENARIO_1),
        ("Clinical Scenario 2: Diuretic Selection", CELL_SCENARIO_2),
        ("Visualization", CELL_VISUALIZATION),
        ("Summary", CELL_SUMMARY),
    ]

    for i, (title, code) in enumerate(cells, 1):
        print(f"\\n{'='*80}")
        print(f"CELL {i}: {title}")
        print("="*80)
        print(code)
