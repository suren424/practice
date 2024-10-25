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

#Function to create a network zone in okta
def create_network_zone(network_zone):
    url =f'{OKTA_DOMAIN}/api/v1/zones'
    headers = {
         'Authorization': f'SSWS {OKTA_API_TOKEN}',
         'content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=json.dumps(network_zone))
    if response.status_code ==200 or response.status_code ==201:
        print(f"Successfully created network zone: {response.json()['id']}")
    else:
        print(f"Error creating network zone: {response.status_code} - {response.text}")

#Prepare that network zone data
gateways =[{'type': 'CIDR', 'value': ip['ip']} for ip_list in ['user', 'server'] for ip in network_zone_data['ip_list'][ip_list] if 'ip' in ip]

network_zone = {
     'name': 'empipzone1',
     #'gateways': [{'type': 'CIDR', 'value':ip['ip']} for ip in network_zone_data ['ip_list']['user'] if 'ip' in ip],
     'gateways':gateways,
     'type':'IP',
     'usage':'POLICY',
     'status':'ACTIVE'
}                                         

#Validate the network zone data
if not network_zone['gateways']:
   raise ValueError("Gateways cannot be empty")

# Create the network zone
create_network_zone(network_zone)

