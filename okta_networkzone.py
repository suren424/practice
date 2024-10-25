import requests # type: ignore
import json
from okta.client import Client as OktaClient # type: ignore

# Configuration
OKTA_ORG_URL = "https://dev-51949121.okta.com"
OKTA_API_TOKEN = "00xHNsRPUUxlX6enklglWmB0LUWLuUiro7EftJdP0d"
S3_JSON_URL = 'https://testiam24.s3.us-east-1.amazonaws.com/iplist.json'

# Initialize Okta client
config = {
    'orgUrl' : OKTA_ORG_URL,
    'token' : OKTA_API_TOKEN
}
okta_client = OktaClient (config)

#Fetch the JSON file from the public s3 url
response = requests.get(S3_JSON_URL)
if response.status_code != 200:
    raise Exception(f"Failed to fetch JSON file: {response.status_code}")

network_zones_data = response.json()

#Function to create a network zone in okta
async def create_network_zone(network_zone):
    try:
        result, resp, err = await okta_client.create_network_zone(network_zone)
        if err:
            print(f"Error creating network zone {err}")
        else:
            print(f"Successfully created network zone: {result['id']}")
    except Exception as e:
           print(f"Exception occured: {e}")

#Prepare that network zone data
network_zone = {
     'name': network_zones_data['empipzone'],
     'gateways':network_zones_data['gateways'],
     'proxies':network_zones_data['proxies'],
     'type':network_zones_data['type'],
     'usage':network_zones_data['usage'],
     'status':network_zones_data['status']
}                                         

# Create the network zone
import asyncio
asyncio.run(create_network_zone(network_zone))

