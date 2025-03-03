#!/usr/bin/env python3

# Requirements:
#
# config.py file that contains a variable google_api_key
#   google_api_key needs access to googlemaps geocode api as well as the timezone functions
#
# sites.csv which contains the following headers:
#   site_name,site_address,site_groups,rf_template_id,spoke_template_name,network_template_name

import csv
import requests
import urllib.parse
import os
import config
import time
import json
import sys
from pprint import pprint
from getpass import getuser
import urllib3


import logging

# Configure the logging
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Set the log message format
    handlers=[
        logging.FileHandler('mist_api.log'),  # Log messages to a file
        #logging.StreamHandler()  # Also print messages to the console
    ]
)

# Turn off warnings to screen for insecure site ( Thanks Umbrella )
# You only need this if you get an SSL error due to corporate security stuff
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# This can be used if you do not want to hard-code your ENV API key
os.environ['GOOGLE_API_KEY'] = config.google_api_key
os.environ['MIST_API_URL'] = config.mist_api_url
os.environ['MIST_API_KEY'] = config.mist_api_key
os.environ['MIST_ORG'] = config.mist_org

# module import needs to occur after setting os.environ variable
import geocoder

class MistAPI(object):
    def __init__(self, host: str, org: str):
        self.host = host
        self.org = org
        self.header = ""

class MistAPIToken(MistAPI):
    def __init__(self, host: str, org: str, mist_api_token: str):
        """

        :param host: api host: ex api.mist.com
        :param org: org_id: example xxxxxxx-xxxx-xxx-xxxxxxxxx
        :param mist_api_token: mist API token "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        """
        super(MistAPIToken, self).__init__(host, org)
        self.mist_api_token = mist_api_token
        self.header = {"Authorization": f"Token {mist_api_token}"}
        logging.info(f"Mist API Token: {mist_api_token}\n")


class Mist:
    def __init__(self, mist_api: MistAPI):
        """

        :param mist_api: MistAPI object or inherited method like MistAPIToken
        """
        self.mistAPI = mist_api

    def http_get(self, url):
        """

        :param url: url extension.  Example: /api/v1/self
        :return: requests response object
        """
        try:
            header = {**{"content-type": "application/json"}, **self.mistAPI.header}
            my_url = f"https://{self.mistAPI.host}{url}"
            response = requests.get(my_url, headers=header, verify=False)
            logging.info(f'Response is {response}\n')
            return response
        except Exception as e:
            print(e)
            logging.info(f'Got an error on response {e}\n')
            return None

    def http_post(self, url: str, body: dict):
        """

        :param url: url extension.  Example: /api/v1/self
        :param body: dictionary formatted body for a post
        :return:
        """
        response = None
        try:
            header = {**{"content-type": "application/json"}, **self.mistAPI.header}
            my_url = f"https://{self.mistAPI.host}{url}"
            response = requests.post(my_url, headers=header, data=json.dumps(body), verify=False)
            logging.info(f'Response for http_post is {response}\n')
        except Exception as e:
            logging.info(f'Got an error for http_post and it was {e}\n')
            print(e)
        return response

    def http_put(self, url: str, body: dict):
        """

        :param url: url extension.  Example: /api/v1/self
        :param body: dictionary formatted body for a post
        :return:
        """
        response = None
        try:
            header = {**{"content-type": "application/json"}, **self.mistAPI.header}
            my_url = f"https://{self.mistAPI.host}{url}"
            response = requests.put(my_url, headers=header, data=json.dumps(body), verify=False)
        except Exception as e:
            print(e)
        return response

    def verify_self(self):
        """

        :return: verifies that API credential successfully return a /api/v1/self
        """
        try:
            results = self.http_get("/api/v1/self")
            if results.status_code == 200:
                return True
        except Exception as e:
            print(e)
            return False

    def get_rf_templates(self):
        """

        :return: returns a list of dictionay rf_templates
        """
        rf_templates = None
        try:
            rf_templates = self.http_get(f"/api/v1/orgs/{self.mistAPI.org}/rftemplates").json()
        except Exception as e:
            print(e)
        return rf_templates

    def get_rftemplate_by_name(self, rf_template_name: str):
        """

        :param rf_template_name: Name of the RF Template
        :return: rf template dictionary
        """
        rf_templates = self.get_rf_templates()
        return next(item for item in rf_templates if item["name"] == rf_template_name)

    # Added Nov 2022 - Fry
    def get_spoke_templates(self):
        """

        :return: returns a list of dictionary gateway templates
        """
        gateway_templates = None
        try:
            gateway_templates = self.http_get(f"/api/v1/orgs/{self.mistAPI.org}/gatewaytemplates").json()
        except Exception as e:
            print(e)
        return gateway_templates

    def get_spoke_template_by_name(self, spoke_template_name: str):
        """

        :param spoke_template_name: Name of the WAN Edge SpokeTemplate
        :return: gateway template dictionary
        """
        gateway_templates = self.get_spoke_templates()
        return next(item for item in gateway_templates if item["name"] == spoke_template_name)

    def get_network_template(self):
        """

        :return: returns a list of dictionary gateway templates
        """
        network_templates = None
        try:
            network_templates = self.http_get(f"/api/v1/orgs/{self.mistAPI.org}/networktemplates").json()
        except Exception as e:
            print(e)
        return network_templates

    def get_network_template_by_name(self, network_template_name: str):
        """

        :param network_template_name: Name of the Switch Template
        :return: gateway template dictionary
        """
        network_templates = self.get_network_template()
        return next(item for item in network_templates if item["name"] == network_template_name)

    def get_site_information(self):
        """
        :return: returns a list of dictionary of the sites
        """
        network_sites = None
        try:
            network_sites = self.http_get(f"/api/v1/orgs/{self.mistAPI.org}/sites").json()
        except Exception as e:
            print(e)
        return network_sites

    def get_site_by_name(self, network_site: str):
        """

        :param network_site: This is the name of the site that we just created
        :return: return site id
        """
        network_sites = self.get_site_information()
        return next(item for item in network_sites if item["name"] == network_site)

    def create_site(self, body):
        """

        :param body: properly formatted body for a site creation
        :return: requests response object
        """
        response = self.http_post(f"/api/v1/orgs/{self.mistAPI.org}/sites", body)
        return response

    def update_site(self, site_body, new_site_id):
        """

        :param body: properly formatted body for a site creation
        :return: requests response object
        """
        response = self.http_put(f"/api/v1/sites/{new_site_id}/setting", site_body)
        return response

def get_site_vars(network_vars):
    with open(network_vars, 'r') as _json_file:
        site_vars = json.load(_json_file)
    #pprint(site_vars)
    #time2pause()
    return(site_vars)

def get_parser():
    """

    :return: parser for argparse
    """
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Mist site creation tool")
    parser.add_argument(
        "-k", "--key", dest="mist_api_key", help="Mist API Key", type=str, required=True
    )
    parser.add_argument(
        "-o", "--org", dest="mist_org", help="Mist Org ID", type=str, required=True
    )
    parser.add_argument(
        "-e", "--EU", dest="mist_europe", help="Mist EU Environment", required=False
    )
    return parser


def encode_address(address: str):
    """

    :param address: normally formatted address
    :return: url encoded string
    """
    return urllib.parse.quote(address)


def get_google_timezone(lat: float, lng: float):
    """
    :param lat: float lattitude
    :param lng: float longitdue
    :return: str with timezone
    """
    g_url = "https://maps.googleapis.com/maps/api/timezone/json?location="
    try:
        response = requests.get(
            f"{g_url}{lat},{lng}&timestamp={int(time.time())}&key={config.google_api_key}")
        data = response.json()
        results = data['timeZoneId']
        return results
    except Exception as e:
        print(e)
        return None


def get_google_geoinfo(address: str):
    """

    :param address: string with site address
    :return: dictionary with geocode info formatted for body
    """
    try:
        gaddr = geocoder.google(address)
        results = {
            'address': gaddr.address,
            'latlng': {
                'lat': gaddr.lat,
                'lng': gaddr.lng,
            },
            'country_code': gaddr.country
        }
        return results
    except Exception as e:
        print(e)
        return None


#def main(argv):
def main():
    successful_sites = []
    failed_sites = []
    created_site_id = []
    created_site_id_list = []
    mist_api_key = config.mist_api_key
    org = config.mist_org
    host = config.mist_api_url
    '''
    if argv.mist_europe is not None:
        host = "api.eu.mist.com"
    else:
        host = "api.ac2.mist.com"
    '''
    site_data = read_csv("sites.csv")
    logging.info(f'Loaded {site_data}')

    # mist_api = MistAPIToken(host, mist_api_key)
    mist_api = MistAPIToken(host, org, mist_api_key)
    mist_connector = Mist(mist_api)
    api_verify = False
    try:
        api_verify = mist_connector.verify_self()
    except Exception as e:
        print(e)
    if api_verify:

        for site in site_data:
            site_body = {}
            body = get_google_geoinfo(site['site_address'])
            body['name'] = site['site_name']
            body['timezone'] = get_google_timezone(body['latlng']['lat'], body['latlng']['lng'])
            print('Checking for rf_template_name\n')
            if site['rf_template_name'] != "":
                body['rftemplate_id'] = mist_connector.get_rftemplate_by_name(site['rf_template_name'])['id']

            print('Checking for spoke_template_name\n')
            if site['spoke_template_name'] != "":
                body['gatewaytemplate_id'] = mist_connector.get_spoke_template_by_name(site['spoke_template_name'])['id']

            print('Checking for network_template_name\n')
            if site['network_template_name'] != "":
                body['networktemplate_id'] = mist_connector.get_network_template_by_name(site['network_template_name'])['id']


            body['notes'] = f'Added by {getuser()} using site_creator script.\n'

            #pprint(f'This is what we just generated for {site["site_name"]} \n')
            #_body_data = json.dumps(body, indent=2)
            #time2pause()

            results = mist_connector.create_site(body)
            if results.status_code == 200:
                successful_sites.append(body)
            else:
                failed_sites.append(body)

            # Checking for site variables and adding them to the site config

            print('Checking to see what ID was created\n')
            new_site_id = mist_connector.get_site_by_name(site['site_name'])['id']
            # print(new_site_id)

            logging.info(f'Checking for site variables \n - {site["network_vars"]=}')
            print(f'Checking for site variables \n - {site["network_vars"]}')
            if site['network_vars'] != '':
                logging.info(f'If we are here, we have site vars?')
                site_body['vars'] = get_site_vars((site['network_vars']))
                logging.info(f"Site Body = {site_body['vars']}")
                print('Applying site variables.\n')
                results = mist_connector.update_site(site_body,new_site_id)
            #print(results)


            created_site_id.append(f'{site["site_name"]} has ID {new_site_id}\n')
            created_site_id_list.append(f'"{new_site_id}",')
            #time2pause()

        print("Successful sites: ")
        for site in successful_sites:
            print(f'\t{site["name"]}')
        print("\nFailed Sites: ")
        for site in failed_sites:
            print(f'\t {site["name"]}')


        print('\n\nWe created the following Sites and Site IDs.')
        for _site_ids in created_site_id:
            print(f'\t{_site_ids}')
        logging.info(created_site_id_list)
        with open("site_created.txt", 'w') as outfile:
            for item in created_site_id_list:
                item_new = item.replace('"',"")
                item_new = item_new.strip(",")
                outfile.write(f'{item_new}\n')

    else:
        print('Check API Key - key did not verify.\n')


def read_csv(filename):
    """

    :param filename: string
    :return: list of site dictionaries
    """
    with open(filename) as csv_file:
        reader = csv.DictReader(csv_file)
        site_data = [record for record in reader]
    #print(site_data)
    return site_data

def time2pause():
    stopprogram = input('Please hit enter to continue to \'q\' to quit: ')
    if stopprogram == "q":
        print('\nQuitting...')
        sys.exit()

if __name__ == '__main__':
    # Deprecated the below functions when moving all the data to the config.py file
    #my_parser = get_parser()
    #my_args = my_parser.parse_args()
    #print(my_args)
    #print(type(my_args))
    #main(my_args)
    main()
