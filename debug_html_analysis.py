#!/usr/bin/env python3
"""
Analyze the debug HTML to understand why severity extraction is failing
"""
from bs4 import BeautifulSoup

# Read the debug HTML file
with open('debug_page_no_severity_found_20251124_011947.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

print("="*60)
print("ANALYZING DEBUG HTML FOR SEVERITY EXTRACTION")
print("="*60)

# Step 1: Look for "Interactions between your drugs" heading
print("\n1. Looking for 'Interactions between your drugs' heading...")
headings = soup.find_all('h2')
drug_interaction_heading = None
for h2 in headings:
    if "Interactions between your drugs" in h2.get_text():
        drug_interaction_heading = h2
        print(f"   ✓ Found heading: {h2.get_text()}")
        break

if not drug_interaction_heading:
    print("   ✗ Heading not found!")
    exit(1)

# Step 2: Get the next sibling div
print("\n2. Looking for interaction wrapper div (next sibling)...")
next_sibling = drug_interaction_heading.find_next_sibling()
print(f"   Next sibling tag: {next_sibling.name if next_sibling else 'None'}")
if next_sibling:
    print(f"   Next sibling classes: {next_sibling.get('class', [])}")

# Step 3: Use CSS selector to find all interactions-reference-wrapper divs
print("\n3. Finding all div.interactions-reference-wrapper elements...")
all_wrappers = soup.find_all('div', class_='interactions-reference-wrapper')
print(f"   Found {len(all_wrappers)} wrapper divs")

for i, wrapper in enumerate(all_wrappers):
    print(f"\n   Wrapper {i+1}:")
    # Find the preceding h2 to see what section this is
    prev_h2 = wrapper.find_previous('h2')
    if prev_h2:
        print(f"     Preceding heading: {prev_h2.get_text()}")

    # Look for severity labels in this wrapper
    severity_labels = wrapper.find_all('span', class_='ddc-status-label')
    print(f"     Severity labels found: {len(severity_labels)}")

    for label in severity_labels:
        classes = label.get('class', [])
        text = label.get_text().strip()
        print(f"       - Classes: {classes}")
        print(f"       - Text: '{text}'")

        # Check for severity category in classes
        if 'status-category-major' in classes:
            print(f"       - Severity: MAJOR")
        elif 'status-category-moderate' in classes:
            print(f"       - Severity: MODERATE")
        elif 'status-category-minor' in classes:
            print(f"       - Severity: MINOR")

# Step 4: Specifically analyze the first wrapper (should be drug-drug interactions)
print("\n4. Detailed analysis of first wrapper (drug-drug interactions)...")
if all_wrappers:
    first_wrapper = all_wrappers[0]

    # Check if it's under "Interactions between your drugs"
    prev_h2 = first_wrapper.find_previous('h2')
    if prev_h2 and "Interactions between your drugs" in prev_h2.get_text():
        print("   ✓ First wrapper is under 'Interactions between your drugs'")

        # Try different selector strategies
        print("\n   Trying different selector strategies:")

        # Strategy 1: Direct span.ddc-status-label
        labels_1 = first_wrapper.select('span.ddc-status-label')
        print(f"     span.ddc-status-label: {len(labels_1)} found")
        for label in labels_1:
            print(f"       Text: '{label.get_text().strip()}', Classes: {label.get('class')}")

        # Strategy 2: All spans
        all_spans = first_wrapper.find_all('span')
        print(f"     All spans: {len(all_spans)} found")
        moderate_spans = [s for s in all_spans if 'moderate' in s.get_text().lower()]
        print(f"     Spans with 'moderate' text: {len(moderate_spans)}")
        for span in moderate_spans:
            print(f"       Text: '{span.get_text().strip()}', Classes: {span.get('class', [])}")

        # Strategy 3: Nested div > div > span
        nested_spans = first_wrapper.select('div > div > span')
        print(f"     div > div > span: {len(nested_spans)} found")
        severity_spans = [s for s in nested_spans if s.get_text().strip().upper() in ['MAJOR', 'MODERATE', 'MINOR']]
        print(f"     With severity text: {len(severity_spans)}")
        for span in severity_spans:
            print(f"       Text: '{span.get_text().strip()}', Classes: {span.get('class', [])}")
    else:
        print("   ✗ First wrapper is NOT under 'Interactions between your drugs'")
        print(f"     It's under: {prev_h2.get_text() if prev_h2 else 'Unknown'}")

print("\n" + "="*60)
print("ANALYSIS COMPLETE")
print("="*60)
