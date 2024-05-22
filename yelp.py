import requests
import csv
import time

# List of example states and their abbreviations
states = [
    "New York, NY",
    "Los Angeles, CA",
    "Chicago, IL",
    "Houston, TX",
    "Phoenix, AZ"
    # Add more states as needed
]

base_url = "https://www.yelp.com/search/snippet"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_clinic_data(state):
    clinics = []
    start = 0
    while True:
        params = {
            'find_desc': 'Med Clinics',
            'find_loc': state,
            'start': start
        }
        response = requests.get(base_url, headers=headers, params=params)
        if response.status_code != 200:
            break

        data = response.json()
        search_results = data['searchPageProps']['rightRailProps']['searchMapProps']['hovercardData']
        if not search_results:
            break

        for result in search_results:
            result = search_results[result]
            if result and result.get('phone'):
                clinic = {
                    'name': result.get('name'),
                    'location': result.get('addressLines', []),
                    'phone': result.get('phone'),
                    'email': 'N/A'  # Yelp typically does not provide emails
                }
                clinics.append(clinic)

        start += 10  # Move to the next page
        if len(clinics) >= 2000:
            break
        time.sleep(1)  # Respectful scraping

    return clinics

def save_to_csv(clinics, filename='clinics.csv'):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Name', 'Location', 'Phone', 'Email']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for clinic in clinics:
            writer.writerow({
                'Name': clinic['name'],
                'Location': ", ".join(clinic['location']),
                'Phone': clinic['phone'],
                'Email': clinic['email']
            })

all_clinics = []

for state in states:
    state_clinics = get_clinic_data(state)
    all_clinics.extend(state_clinics)
    if len(all_clinics) >= 2000:
        break

save_to_csv(all_clinics[:2000])
