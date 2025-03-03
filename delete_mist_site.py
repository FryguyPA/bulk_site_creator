import requests
import urllib3
import logging
import os
import config
from pprint import pprint as pp

'''
This script will delete the sites listed in the site_created.txt file.  
You can either edit this file manually, or you can use the output from
the site_creator.py file. 

We use the config.py for the API, ORG, and Mist URLs

'''

# Configure logging
logging.basicConfig(
    filename="mist_delete_api.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Turn off warnings to screen for insecure site ( Thanks Umbrella )
# You only need this if you get an SSL error due to corporate security stuff
try:
    if config.ssldisable=='yes':
        print('Disabling SSL verification per config.py config')
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except:
    pass

# This can be used if you do not want to hard-code your ENV API key
os.environ['MIST_API_URL'] = config.mist_api_url
os.environ['MIST_API_KEY'] = config.mist_api_key
os.environ['MIST_ORG'] = config.mist_org

# Read the file into a list
with open("site_created.txt", "r") as file:
    SITE_ID_LIST = [line.strip() for line in file]

# using the config.py file, read the following values
API_URL = config.mist_api_url
API_KEY = config.mist_api_key
MIST_ORG = config.mist_org

# Define headers with authentication
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Token {API_KEY}"
}

# Query the API and get a list of sites, we will use this to match site_id to a site_name
response = requests.get(f"https://{API_URL}/api/v1/orgs/{MIST_ORG}/sites", verify=False, headers=headers)
site_data = response.json()
logging.info(f'{site_data=}')

# This is used in case we answer an 'a' for all sites ( hidden option )
riddleanswered = ''

# Iterate over the list that we read in earlier
for SITE_ID in SITE_ID_LIST:
    # API endpoint for deleting a site
    url = f"https://{API_URL}/api/v1/sites/{SITE_ID}"

    # Here we try to match the site, if we do not match, we will skip it as the site may not exist
    try:
        # This is used to match site_id to site_name
        matching_site = next((site for site in site_data if site["id"] == SITE_ID), None)
        site_name = (matching_site['name'])

        logging.info(f"Attempting to delete Mist site:{site_name} - {SITE_ID}")

        riddlemethis = input(f"Are you sure you want to delete Mist site: {site_name} with site id {SITE_ID}? ").strip().lower()

        if riddlemethis == "y" or riddlemethis == "a":
            try:
                # Delete the site
                response = requests.delete(url, headers=headers, verify=False)

                if response.status_code == 200:
                    logging.info(f"Site {SITE_ID} deleted successfully.")
                    print(f"Site {SITE_ID} deleted successfully.")
                else:
                    logging.error(f"Failed to delete site {site_name} - {SITE_ID}. Status Code: {response.status_code}, Response: {response.text}")
                    print(f"Failed to delete site {site_name} - {SITE_ID}. Status Code: {response.status_code}")

            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed: {e}")
                print(f"Request failed: {e}")
        else:
            continue

    except:
        print(f'{SITE_ID} not found, skipping\n')

