import os
from dotenv import load_dotenv
import requests
import urllib3
import xml.etree.ElementTree as ET
import subprocess

load_dotenv()

PASSCODE = os.environ.get("PASSCODE")

urllib3.disable_warnings()

def check_software(ip):
    headers = {'Authorization': 'basic YWRtaW46NzM2NjgzMjk='}
    
    try:
        soft_xml = requests.get(f'https://{ip}/getxml?location=/Status/SystemUnit/Software/Version', headers=headers, verify=False)
        xml_root = ET.fromstring(soft_xml.text)
        print(soft_xml.text)
        parsed_version = xml_root[0][0][0].text.replace('ce','').split('.')
        return parsed_version
    except requests.exceptions.HTTPError as err:
        print(err.response)
        return False

def check_hardware(ip):
    headers = {'Authorization': f'basic {PASSCODE}'}
    
    hardware_list = {
        'pro': ['Codec Pro', 'Room Bar'],
        'kit': ['Room Kit', 'Room Kit Mini', 'Codec Plus'],
        'SX80': 'SX80'
    }

    try:
        soft_xml = requests.get(f'http://{ip}/getxml?location=/Status/SystemUnit/ProductPlatform', headers=headers, verify=False)
        print(soft_xml.text)
        xml_root = ET.fromstring(soft_xml.text)
        parsed_version = xml_root[0][0].text
        if (parsed_version == 'SX80'):
            print('SX80 found')
            return 'SX80'
        for unit in hardware_list['pro']:
            if (parsed_version == unit):
                print('Pro found')
                return 'pro'
        for unit in hardware_list['kit']:
            if (parsed_version == unit):
                print('Kit found')
                return 'kit'
        
        print(parsed_version)
    except requests.exceptions.HTTPError as err:
        print(err.response)
        return False

def check_system_name(ip):
    headers = {'Authorization': f'basic {PASSCODE}'}

    try:
        xml = requests.get(f'https://{ip}/getxml?location=/Configuration/SystemUnit/Name', headers=headers, verify=False)
        xml_root = ET.fromstring(xml.text)
        print(xml_root.text)
        system_name = xml_root[0][0].text
        print(f'Codec Name Found: {system_name}')
        return system_name
    except requests.exceptions.HTTPError as err:
        print(err.response)
        return False

# check_hardware('172.17.64.174')

# check_software('172.16.131.60')

# check_system_name('172.16.131.191')

ping = subprocess.run(["ping","-c","1","172.16.131.191"], capture_output=True)

print(ping.returncode)

if __name__ == '__main__':
    print(ping.returncode)