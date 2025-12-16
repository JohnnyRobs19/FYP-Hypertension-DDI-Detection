"""
Add Part 2: Knowledge-Driven Safer Medication Pathway cells to all three notebooks
Uses the new XAI Framework (Non-interactive version)
"""

import json
from PART_2_PATHWAY_RECOMMENDATION_CELLS import (
    CELL_LOAD_XAI,
    CELL_SEVERITY_MAPPING,
    CELL_PREDICTIONS,
    CELL_XAI_CONTEXT,
    CELL_SCENARIO_1,
    CELL_SCENARIO_2,
    CELL_SCENARIO_3,
    CELL_VISUALIZATION,
    CELL_SUMMARY
)

def create_markdown_cell(text):
    """Create a markdown cell"""
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": text
    }

def create_code_cell(code):
    """Create a code cell"""
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [code]
    }

def add_part2_to_notebook(notebook_path, model_name):
    """Add Part 2 cells to a notebook"""

    print(f"\n{'='*80}")
    print(f"Processing: {notebook_path}")
    print(f"Model: {model_name}")
    print("="*80)

    # Load notebook
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
    except Exception as e:
        print(f"❌ Error loading notebook: {e}")
        return False

    # Remove existing Part 2 cells if they exist
    original_count = len(notebook['cells'])
    part2_started = False
    new_cells = []

    for cell in notebook['cells']:
        if cell.get('cell_type') == 'markdown':
            content = ''.join(cell.get('source', []))
            if 'PART 2' in content or 'Part 2' in content:
                part2_started = True
                print(f"  Found existing Part 2 section - removing...")
                continue

        if not part2_started:
            new_cells.append(cell)

    notebook['cells'] = new_cells
    removed = original_count - len(new_cells)
    if removed > 0:
        print(f"  Removed {removed} existing Part 2 cells")

    # Create Part 2 cells
    part2_cells = [
        create_markdown_cell([
            f"# Part 2: Knowledge-Driven Safer Medication Pathway Recommendation\n",
            "\n",
            f"## Section 3.5.4: Knowledge-Driven Explainability (XAI) Framework\n",
            "\n",
            f"**Integration with {model_name}:**\n",
            "- Part 1: ML model predicts DDI severity (Major/Moderate/Minor)\n",
            "- Part 2: XAI framework provides evidence-based clinical context\n",
            "- Result: Predictions + Actionable clinical recommendations\n",
            "\n",
            "**XAI Rules Implemented:**\n",
            "- Rule A: ACEI vs ARB Mortality Benefit (Alcocer 2023)\n",
            "- Rule B: ACEI Tolerability & Cough Risk (Hu 2023)\n",
            "- Rule C: CCB+RAAS Combination Therapy (Makani 2011)\n",
            "- Rule D: Diuretic Efficacy - Indapamide vs HCTZ (Roush 2015)\n",
            "- Rule E: Beta-Blocker Phenotype Targeting (Mahfoud 2024)\n"
        ]),

        create_markdown_cell(["## Step 1: Load XAI-Enhanced Dataset\n"]),
        create_code_cell([CELL_LOAD_XAI]),

        create_markdown_cell(["## Step 2: Define Severity-to-Risk Mapping\n"]),
        create_code_cell([CELL_SEVERITY_MAPPING]),

        create_markdown_cell([
            f"## Step 3: Generate Predictions Using Trained {model_name} Model\n"
        ]),
        create_code_cell([CELL_PREDICTIONS]),

        create_markdown_cell(["## Step 4: Integrate XAI Clinical Context with Predictions\n"]),
        create_code_cell([CELL_XAI_CONTEXT]),

        create_markdown_cell([
            "## Clinical Scenario 1: ACEI/ARB + CCB Combination Therapy\n",
            "\n",
            "**Clinical Question:** For a patient requiring RAAS blocker + CCB combination:\n",
            "- Which combination is safest?\n",
            "- What's the clinical evidence?\n"
        ]),
        create_code_cell([CELL_SCENARIO_1]),

        create_markdown_cell([
            "## Clinical Scenario 2: Diuretic Selection (Indapamide vs HCTZ)\n",
            "\n",
            "**Clinical Question:** For a patient requiring diuretic therapy:\n",
            "- Indapamide or Hydrochlorothiazide?\n",
            "- What's the outcome evidence?\n"
        ]),
        create_code_cell([CELL_SCENARIO_2]),

        create_markdown_cell([
            "## Clinical Scenario 3: Beta-Blocker Phenotype Targeting\n",
            "\n",
            "**Clinical Question:** For a patient with high resting heart rate (>80 bpm):\n",
            "- Are beta-blockers indicated?\n",
            "- What's the phenotype-based rationale?\n"
        ]),
        create_code_cell([CELL_SCENARIO_3]),

        create_markdown_cell([
            "## Visualization: Predictions with XAI Coverage\n",
            "\n",
            "Visualize how XAI clinical context enhances ML predictions across drug class combinations.\n"
        ]),
        create_code_cell([CELL_VISUALIZATION]),

        create_markdown_cell(["## Part 2 Summary: Knowledge-Driven Clinical Decision Support\n"]),
        create_code_cell([CELL_SUMMARY]),
    ]

    # Append Part 2 cells to notebook
    notebook['cells'].extend(part2_cells)

    # Save updated notebook
    try:
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1, ensure_ascii=False)
        print(f"✅ Successfully added Part 2 to {notebook_path}")
        print(f"   Added {len(part2_cells)} new cells")
        print(f"   Total cells in notebook: {len(notebook['cells'])}")
        return True
    except Exception as e:
        print(f"❌ Error saving notebook: {e}")
        return False

def main():
    """Add Part 2 to all three notebooks"""

    notebooks = [
        ("Decision_Tree_DDI_Analysis_and_Training.ipynb", "Decision Tree"),
        ("Random_Forest_DDI_Analysis_and_Training.ipynb", "Random Forest"),
        ("XGBoost_DDI_Analysis_and_Training.ipynb", "XGBoost"),
    ]

    print("="*80)
    print("ADDING PART 2: KNOWLEDGE-DRIVEN XAI FRAMEWORK TO NOTEBOOKS")
    print("="*80)
    print("\nUpdating notebooks with Part 2 cells:")
    for nb, model in notebooks:
        print(f"  • {nb} ({model})")

    print(f"\nPart 2 includes 17 new cells:")
    print("  • 8 markdown cells (titles/explanations)")
    print("  • 9 code cells (XAI implementation)")

    # Process each notebook
    success_count = 0
    for notebook_path, model_name in notebooks:
        if add_part2_to_notebook(notebook_path, model_name):
            success_count += 1

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Successfully updated: {success_count}/{len(notebooks)} notebooks")

    if success_count == len(notebooks):
        print("\n✅ All notebooks updated successfully!")
        print("\nNext steps:")
        print("  1. Open each notebook in Jupyter")
        print("  2. Run Part 2 cells to see XAI framework in action")
        print("  3. Review clinical recommendations and XAI context")
    else:
        print(f"\n⚠️  {len(notebooks) - success_count} notebook(s) had issues")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main()
