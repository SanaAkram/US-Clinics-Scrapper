import csv


def find_duplicates_and_uniques(input_filename, duplicates_filename, uniques_filename):
    fieldnames = ['Clinics', 'Number', 'Location']

    # Load the clinic data from the CSV file
    with open(input_filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        clinics = [row for row in reader]

    unique_clinics = []
    duplicate_clinics = []
    unique_checker = set()

    # Identify duplicates and unique entries
    for clinic in clinics:
        key = (clinic['Clinics'], clinic['Number'], clinic['Location'])
        if key in unique_checker:
            duplicate_clinics.append(clinic)
        else:
            unique_checker.add(key)
            unique_clinics.append(clinic)

    # Save unique entries to a new CSV file
    with open(uniques_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for clinic in unique_clinics:
            writer.writerow(clinic)

    # Save duplicate entries to a new CSV file
    with open(duplicates_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for clinic in duplicate_clinics:
            writer.writerow(clinic)


# Example usage:
input_filename = 'Clinics_Data - USA - Clinics - all data.csv'
duplicates_filename = 'Duplicate_Clinics.csv'
uniques_filename = 'Unique_Clinics.csv'

find_duplicates_and_uniques(input_filename, duplicates_filename, uniques_filename)
