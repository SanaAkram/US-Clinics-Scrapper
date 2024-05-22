import requests
from bs4 import BeautifulSoup
import time
import json
# URL of the UCSF Health Clinics page
url = 'https://www.ucsfhealth.org/clinics'
response = requests.get(url)
import csv
clinics = []

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    for div in soup.find_all('div', class_='master-finder-rollup-links-container'):
        letter = div['id']

        for li in div.find_all('li'):
            clinic_name = li.find('a').text.strip()
            clinic_url = 'https://www.ucsfhealth.org' + li.find('a')['href']
            clinics.append({'name': clinic_name, 'url': clinic_url})
else:
    print(f'Failed to retrieve the page. Status code: {response.status_code}')


def extract_data_from_jsonld(script_tag):
    jsonld = json.loads(script_tag.string)
    clinics = []
    try:
        name = jsonld.get('name', 'N/A')
        phone = jsonld.get('telephone', 'N/A')
        address = jsonld.get('address', {})
        if len(address) == 1:
            address = address[0]
        # Ensure addresses is a list
        if not isinstance(address, dict) and not isinstance(phone, dict):
            phone = phone[0]
            address = address[0]
            location = address.get('addressLocality', 'N/A')

            clinic_info = {
                'name': name,
                'phone': phone,
                'location': location
            }
            clinics.append(clinic_info)
            return clinics

        location = address.get('addressLocality', 'N/A')

        clinic_info = {
            'name': name,
            'phone': phone,
            'location': location
        }
        clinics.append(clinic_info)

        return clinics
    except Exception as e:
        print(f"Error: {e}")

def write_to_csv(clinics_data, filename):
    file_exists = False
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            csvfile.seek(0)
            file_exists = bool(csvfile.read(1))
    except FileNotFoundError:
        pass

    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Name', 'Phone', 'Email', 'Location']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        for clinic in clinics_data:
            writer.writerow({
                'Name': clinic['name'],
                'Phone': clinic['phone'],
                'Email': '',
                'Location': clinic['location']
            })
def get_clinic_details(clinic_url):
    response = requests.get(clinic_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        phone_div = soup.find('div', class_='clinic-phone-num')
        phone = phone_div.text.strip() if phone_div else 'No phone found'
        jsonld_script = soup.find('script', type='application/ld+json')
        if jsonld_script:
            clinics = extract_data_from_jsonld(jsonld_script)
            return clinics
        else:
            print("JSON-LD script tag not found.")
        # Check for advanced map card structure
        # card_content = soup.find('div', class_='card-content')
        # if card_content:
        #     phone_span = card_content.find('div', class_='font-smaller', text=lambda x: x and '(415)' in x)
        # address_p = card_content.find_all('p')[1] if len(card_content.find_all('p')) > 1 else None
        #     phone = phone_span.text.strip() if phone_span else phone
        #     address = address_p.text.strip() if address_p else ''

        return phone

    else:
        return 'No address found', 'No phone found'


all_clinic_data = []
# Extract and print clinic details
for clinic_list in clinics:
    clinic = get_clinic_details(clinic_list['url'])
    if clinic:
        all_clinic_data.append(clinic[0])
        print(f'{clinic_list}')
        time.sleep(1)

filename = 'UCSF_Clinics.csv'
write_to_csv(all_clinic_data, filename)
print(f'Data saved to {filename}')
