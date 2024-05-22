import csv
import requests
import sqlite3
from urllib.parse import quote
import os
# Initialize SQLite database
conn = sqlite3.connect('clinics.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''
CREATE TABLE IF NOT EXISTS clinics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    address TEXT,
    email TEXT,
    location TEXT,
    UNIQUE(name, location)
)
''')


def get_clinics_with_phone_numbers(url, state):
    clinics_with_phone_numbers = []

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        clinics = data['search']['searchResults']['facility']['results']
        for clinic in clinics:
            name = clinic.get('name', '')
            phone = clinic.get('phone', '')
            address_dict = clinic.get('address', {})
            address = f"{address_dict.get('street', '')}, {address_dict.get('city', '')}, {address_dict.get('state', '')} {address_dict.get('zip', '')}"
            email = clinic.get('email', '')
            location = state
            if phone:
                clinic_info = {
                    'name': name if name else 'N/A',
                    'phone': phone if phone else 'N/A',
                    'address': address if address else 'N/A',
                    'email': email if email else 'N/A',
                    'location': location if location else 'N/A'
                }
                clinics_with_phone_numbers.append(clinic_info)
    else:
        print(f"Failed to get data for state: {state}, URL: {url}")

    return clinics_with_phone_numbers


def insert_into_database(clinics_data):
    for clinic in clinics_data:
        try:
            c.execute("INSERT INTO clinics (name, phone, address, email, location) VALUES (?, ?, ?, ?, ?)",
                      (clinic['name'], clinic['phone'], clinic['address'], clinic['email'], clinic['location']))
        except sqlite3.IntegrityError:
            print(f"Duplicate entry found for clinic: {clinic['name']} in {clinic['location']}")
        except Exception as e:
            print(f"Error inserting clinic: {clinic['name']}, Error: {e}")

    conn.commit()


# Lists of States in USA
us_states = [
    'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida',
    'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland',
    'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada',
    'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma',
    'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
    'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
]

# Base URL for the API
base_api_url = 'https://www.healthgrades.com/api3/usearch?where={},&sessionId=S0a24&requestId=R9f6787a9af1a837e3d&sort.facility=bestmatch&category=facility&cid&hgTrace=false&isPsr=false&isFsr=false&isFirstRequest=false&pageNum=1&userLocalTime=2%3A51&FacilityType=HGUC&distances=National'


def write_to_csv(clinics_data, filename):
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Name', 'Phone', 'Address', 'Email', 'Location']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        # Check if file is empty
            csvfile.seek(0)
            first_char = csvfile.read(1)
            if not first_char:
                # File is empty, write header
                writer.writeheader()

        # Append clinic data
        for clinic in clinics_data:
            writer.writerow({
                'Name': clinic['name'],
                'Phone': clinic['phone'],
                'Address': clinic['address'],
                'Email': clinic['email'],
                'Location': clinic['location']
            })


# Iterate through each state and retrieve clinic data
for state in us_states:
    state_url = base_api_url.format(quote(state))
    print(f"Fetching data for state: {state}")
    clinics_data = get_clinics_with_phone_numbers(state_url, state)
    print(f"Number of clinics found: {len(clinics_data)} for state: {state}")
    # Insert data into database
    # insert_into_database(clinics_data)
    filename = f"{state}_clinics.csv"
    # write_to_csv(clinics_data, filename)
    print(f"Data saved to {filename}")

# Directory containing state CSV files
input_directory = "state_csvs"
# Output file for merged data
output_file = "merged_clinics.csv"


# Function to merge CSV files
def merge_csv_files(input_dir, output_file):
    # List to store data from all state CSV files
    all_data = []

    # Iterate over each file in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".csv"):
            filepath = os.path.join(input_dir, filename)
            # Read data from the current CSV file
            with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                # Append data from the current file to the list
                all_data.extend([row for row in reader])

    # Write the merged data to the output file
    with open(output_file, 'w', newline='', encoding='utf-8') as merged_csvfile:
        fieldnames = ['Name', 'Phone', 'Address', 'Email', 'Location']
        writer = csv.DictWriter(merged_csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_data)
# Close database connection
# Merge CSV files
merge_csv_files(input_directory, output_file)
print("Data merged successfully!")
conn.close()
