from dotenv import load_dotenv
from TokenManager import TokenManager
import os
import warnings
import requests
import json

# Suppress InsecureRequestWarning - these requests are made to your local IQ Gateway, presumably you trust it
warnings.filterwarnings('ignore', category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Load the variables from the .env file
load_dotenv()

# Instantiate token manager and retrieve it
token_manager = TokenManager(expiration_time=3600)
token = token_manager.get_token()
token_manager.close()

# Sample data request from all inverters
data_req_headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {token}'
}
resp = requests.get(
    os.getenv('ENPHASE_IQ_GATEWAY_IP') + '/api/v1/production/inverters', # Works
    # os.getenv('ENPHASE_IQ_GATEWAY_IP') + '/ivp/meters/reports/consumption', # Works
    # os.getenv('ENPHASE_IQ_GATEWAY_IP') + '/ivp/meters/readings', # Works
    # More info on why this route is not working in README
    # os.getenv('ENPHASE_IQ_GATEWAY_IP') + '/ivp/pdm/energy', # AUTH REQUIRED err
    headers=data_req_headers,
    verify=False
)
response_data = json.loads(resp.text)
print(response_data)