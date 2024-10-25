import requests
import json

# Configuration
S3_JSON_URL = 'https://testiam24.s3.us-east-1.amazonaws.com/iplist.json'
OKTA_DOMAIN = 'https://dev-51949121.okta.com'
OKTA_API_TOKEN = "00xHNsRPUUxlX6enklglWmB0LUWLuUiro7EftJdP0d"

#Fetch the JSON file from the public s3 url
response = requests.get(S3_JSON_URL)
if response.status_code != 200:
    raise Exception(f"Failed to fetch JSON file: {response.status_code}")

network_zone_data = response.json()

#Function to create or update a network zone in okta
def create_or_update_network_zone(network_zone, zone_count,existing_zone_id=None):
    url = f'{OKTA_DOMAIN}/api/v1/zones'
    if existing_zone_id:
        url = f'{url}/{existing_zone_id}'
        method = requests.put
    else:
        method = requests.post

    headers = {
         'Authorization': f'SSWS {OKTA_API_TOKEN}',
         'content-Type': 'application/json'
    }
    response = method(url,headers=headers, data=json.dumps(network_zone))
    if response.status_code in [200, 201]:
        print(f"Successfully created/updated network zone {zone_count}: {response.json()['id']}")
    else:
        print(f"Error creating/updating network zone {zone_count}: {response.status_code} - {response.text}")
# Function to fetch existing network zones from Okta
def fetch_existing_network_zones():
    url = f'{OKTA_DOMAIN}/api/v1/zones'
    headers = {
          'Authorization': f'SSWS {OKTA_API_TOKEN}',
         'content-Type': 'application/json'       
    }
    response = requests.get(url,headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch existing network zones: {response.status_code}")
    return response.json()
# Fetch existing network zones
existing_zones = fetch_existing_network_zones()

#Prepare that network zone data
gateways = []
zone_count = 1
existing_zone_id = None

for ip_list in ['user', 'server']:
    for ip in network_zone_data['ip_list'][ip_list]:
        if 'ip' in ip:
            gateways.append({'type': 'CIDR', 'value': ip['ip']})
            if len(gateways) == 3:
                network_zone = {
                        'name': f'myipzone {zone_count}',
                        'gateways':gateways,
                        'type':'IP',
                        'usage':'POLICY',
                        'status':'ACTIVE'
                }
                # Check if an existing zone matches the current zone name
                for zone in existing_zones:
                    if zone['name'] == network_zone['name']:
                        existing_zone_id =zone['id']
                        break
                create_or_update_network_zone(network_zone, zone_count, existing_zone_id)
                gateways = []
                zone_count += 1
                existing_zone_id = None

#Create or update the last network zone if there are remaining gateways
if gateways:
   network_zone = {
    'name': f'myipzone {zone_count}',
    'gateways': gateways,
    'type':'IP',
    'usage':'POLICY',
    'status':'ACTIVE'
}
# Check if an existing zone mathes the current zone name
for zone in existing_zones:
    if zone['name'] == network_zone['name']:
        existing_zone_id = zone['id']
        break                                        
create_or_update_network_zone(network_zone, zone_count, existing_zone_id)

