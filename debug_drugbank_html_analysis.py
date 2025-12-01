#!/usr/bin/env python3
"""
Analyze the debug HTML to understand DrugBank page structure for severity extraction
"""
from bs4 import BeautifulSoup
import glob
import os


def analyze_latest_debug_html():
    """Analyze the most recent DrugBank debug HTML file"""

    # Find all debug HTML files
    html_files = glob.glob('debug_drugbank_page_*.html')

    if not html_files:
        print("No debug HTML files found. Run debug_drugbank_add_drugs.py first.")
        return

    # Use the most recent file
    latest_file = max(html_files, key=os.path.getctime)
    print(f"Analyzing file: {latest_file}")

    with open(latest_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    print("="*60)
    print("ANALYZING DRUGBANK DEBUG HTML FOR SEVERITY EXTRACTION")
    print("="*60)

    # Step 1: Look for the ddi-widget-body
    print("\n1. Looking for 'ddi-widget-body' container...")
    ddi_widgets = soup.find_all('div', class_='ddi-widget-body')
    print(f"   Found {len(ddi_widgets)} ddi-widget-body containers")

    # Step 2: Look for result containers
    print("\n2. Looking for result containers (form-row mb-3)...")
    result_containers = soup.find_all('div', class_='form-row mb-3')
    if not result_containers:
        result_containers = soup.find_all('div', class_='form-row')
    print(f"   Found {len(result_containers)} result containers")

    # Step 3: Look for severity elements
    print("\n3. Looking for severity indicators...")

    # Strategy 1: Look for elements with 'severity' in class
    severity_by_class = soup.find_all(class_=lambda x: x and 'severity' in x.lower())
    print(f"   Elements with 'severity' in class: {len(severity_by_class)}")
    for i, elem in enumerate(severity_by_class[:5]):
        classes = elem.get('class', [])
        text = elem.get_text().strip()[:50]
        print(f"     {i+1}. Classes: {classes}, Text: '{text}'")

    # Strategy 2: Look for interaction-severity class
    interaction_severity = soup.find_all(class_='interaction-severity')
    print(f"\n   Elements with 'interaction-severity' class: {len(interaction_severity)}")
    for i, elem in enumerate(interaction_severity[:5]):
        classes = elem.get('class', [])
        text = elem.get_text().strip()
        print(f"     {i+1}. Classes: {classes}, Text: '{text}'")

    # Strategy 3: Look for intx-item class
    intx_items = soup.find_all(class_='intx-item')
    print(f"\n   Elements with 'intx-item' class: {len(intx_items)}")
    for i, elem in enumerate(intx_items[:5]):
        classes = elem.get('class', [])
        text = elem.get_text().strip()[:50]
        print(f"     {i+1}. Classes: {classes}, Text: '{text}'")

    # Step 4: Look for card-row header-row
    print("\n4. Looking for header rows...")
    header_rows = soup.find_all('div', class_='card-row header-row')
    if not header_rows:
        header_rows = soup.find_all('div', class_='header-row')
    print(f"   Found {len(header_rows)} header rows")

    for i, row in enumerate(header_rows[:3]):
        print(f"\n   Header row {i+1}:")
        # Find all divs inside this header
        divs = row.find_all('div', recursive=False)
        for j, div in enumerate(divs):
            classes = div.get('class', [])
            text = div.get_text().strip()[:50]
            print(f"     Div {j+1}: Classes: {classes}, Text: '{text}'")

    # Step 5: Look for text containing severity keywords
    print("\n5. Looking for text containing severity keywords...")
    severity_keywords = ['Major', 'Moderate', 'Minor']

    for keyword in severity_keywords:
        elements = soup.find_all(text=lambda t: t and keyword in t)
        print(f"   Elements containing '{keyword}': {len(elements)}")
        if elements:
            for i, elem in enumerate(elements[:3]):
                parent = elem.parent
                parent_name = parent.name if parent else 'None'
                parent_class = parent.get('class', []) if parent else []
                print(f"     {i+1}. Parent: <{parent_name}>, Classes: {parent_class}, Text: '{elem.strip()[:50]}'")

    # Step 6: Check the overall structure
    print("\n6. Analyzing overall structure...")
    if ddi_widgets:
        print("   Analyzing first ddi-widget-body structure:")
        first_widget = ddi_widgets[0]

        # Find form-rows inside
        form_rows = first_widget.find_all('div', class_='form-row', recursive=True)
        print(f"     Form rows inside: {len(form_rows)}")

        if form_rows:
            print("     First form-row structure:")
            first_form = form_rows[0]
            print(f"       Classes: {first_form.get('class', [])}")

            # Find all nested divs
            nested_divs = first_form.find_all('div', recursive=False)
            for i, div in enumerate(nested_divs[:5]):
                classes = div.get('class', [])
                print(f"       Nested div {i+1}: Classes: {classes}")

    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print("\nRecommendations:")
    print("1. Check if the selectors in drugbank_ddi_scraper.py match the found elements")
    print("2. If no severity elements found, the page might not have loaded completely")
    print("3. Run debug_drugbank_add_drugs.py to capture a page with actual results")


if __name__ == "__main__":
    analyze_latest_debug_html()
