import os
from dotenv import load_dotenv
import requests
import urllib3
import xml.etree.ElementTree as ET

load_dotenv()

PASSCODE = os.environ.get("PASSCODE")

urllib3.disable_warnings()

def check_hardware(ip):
    headers = {'Authorization': f'basic {PASSCODE}'}
    
    try:
        soft_xml = requests.get(f'http://{ip}/getxml?location=/Status/SystemUnit/ProductPlatform', headers=headers, verify=False)
        print(soft_xml.text)
        xml_root = ET.fromstring(soft_xml.text)
        parsed_version = xml_root[0][0].text
        print(parsed_version)
        return parsed_version
    except requests.exceptions.HTTPError as err:
        print(err.response)
        return False
    
check_hardware('172.16.131.60')