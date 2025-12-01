import csv

# Read the CSV file
csv_file = 'FYP_Drug_Interaction_Template.csv'

# Read all rows
rows = []
with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames

    num_updates = 0
    for row in reader:
        # Check if DrugsCom_Text is "No drug-drug interactions found"
        if row['DrugsCom_Text'] == 'No drug-drug interactions found':
            row['DrugsCom_Severity'] = 'None'
            num_updates += 1
        rows.append(row)

print(f"Total rows in CSV: {len(rows)}")
print(f"Rows updated: {num_updates}")

# Write the updated data back to the CSV file
with open(csv_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"\nUpdated {num_updates} rows successfully!")
print(f"CSV file '{csv_file}' has been updated.")

# Show a sample of the updated rows
print("\nSample of updated rows:")
count = 0
for row in rows:
    if row['DrugsCom_Text'] == 'No drug-drug interactions found' and count < 10:
        print(f"{row['Drug_A_Name']} + {row['Drug_B_Name']}: DrugsCom_Severity = {row['DrugsCom_Severity']}")
        count += 1
