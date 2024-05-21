import os
from dotenv import load_dotenv
import requests
import xml.etree.ElementTree as ET


#Pulling Environment Variables
load_dotenv()

PASSCODE = os.environ.get('PASSCODE')
PROPATH = os.environ.get('PROPATH')
KITPATH = os.environ.get('KITPATH')

# disable ssl warning, not currently working
# urllib3.disable_warnings(InsecureRequestWarning)

#Defining filenames to be appended to filepath in the upgrade_command_xml() function
kit_versions = {
    '9.15': {'file': 'cmterm-s53200ce9_15_3_22.k3.cop.sgn'},
    '10.19': {'file': 'cmterm-s53200ce10_19_5_6.k3.cop.sgn'},
    '10.15': {'file': 'cmterm-s53200ce10_15_4_1.k3.cop.sgn'},
    '11.5': {'file': 'cmterm-s53200ce11_5_2_4.k4.cop.sha512'},
    '11.9': {'file': 'cmterm-s53200ce11_9_3_1.k4.cop.sha512'},
    '11.14': {'file': 'cmterm-s53200ce11_14_2_3.k4.cop.sha512'}
}

pro_versions = {
    '10.15': {'file': 'cmterm-s53300ce10_15_4_1.k3.cop.sgn'},
    '10.19': {'file': 'cmterm-s53300ce10_19_5_6.k3.cop.sgn'},
    '11.9': {'file': 'cmterm-s53300ce11_9_2_4.k4.cop.sha512'},
    '11.14': {'file': 'cmterm-s53300ce11_14_2_3.k4.cop.sha512'},
}

#Command used to populate XML string to be sent to codec by upgrade command
def upgrade_command_xml(file_path, file_string):
    return f'<Command>\r\n\t<SystemUnit>\r\n\t\t<SoftwareUpgrade>\r\n\t\t\t<URL>{file_path}{file_string}</URL>\r\n\t\t</SoftwareUpgrade>\r\n\t</SystemUnit>\r\n</Command>'


#Checks software version. Used by chain_upgrade() command to determine where to start in the upgrade path
def check_software(ip):
    headers = {'Authorization': 'basic YWRtaW46NzM2NjgzMjk='}
    
    try:
        soft_xml = requests.get(f'https://{ip}/getxml?location=/Status/SystemUnit/Software/Version', headers=headers)
        xml_root = ET.fromstring(soft_xml.text)
        print(soft_xml.text)
        parsed_version = xml_root[0][0][0].text.replace('ce','').split('.')
        return parsed_version
    except requests.exceptions.HTTPError as err:
        print(err.response)
        return False


#Checks hardware version of the codec. Used to determine which upgrade files to use 
def check_hardware(ip):
    headers = {f'Authorization': 'basic {}'}
    
    try:
        soft_xml = requests.get(f'http://{ip}/getxml?location=/Status/SystemUnit/ProductPlatform', headers=headers)
        xml_root = ET.fromstring(soft_xml.text)
        print(soft_xml.text)
        parsed_version = xml_root[0][0].text
        return parsed_version
    except requests.exceptions.HTTPError as err:
        print(err.response)
        return False


def upgrade(version, ip):
    try:
        url = f'http://{ip}/putxml'
        headers = {'Authorization': 'basic YWRtaW46NzM2NjgzMjk='}
        payload = upgrade_command_xml(version)
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        print(response.text)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err.response)
    return False

# check_software('172.16.131.163')
def chain_update(ip):

    software_version = check_software(ip)

    hardware_version = check_hardware(ip)

    if (software_version == False):
        print('Error retrieving code version from codec. Exiting function.')
        return
    
    if (software_version == False):
        print('Error retrieving hardware version from codec. Exiting function.')

    # Returns chain update function if code is on the latest version. Changes will need to be added later to allow for dynamic edits to code versions as newer ones come out.
    if (software_version[0] == 11 and software_version[1] == 14):
        return

    
    #Comparing code versions
    if (software_version[0] < 10):
        if (software_version[1] < 15):
            print('upgrade to version 9.15.3.22')
            upgrade()
        else:
            print('Upgrade to version 10.15.4')
    elif (software_version[0] == 10):
        if (software_version[1] < 15):
            print('Upgrade to version 10.15.4')
        elif (software_version[1] >= 15 and software_version[1] < 19):
            print('Upgrade to version 10.19.4.2')
        else:
            print('Upgrade to version 11.1.2.4')
    elif (software_version[0] == 11):
        if (software_version[1] < 9):
            print('Upgrade to version 11.9')
        elif (software_version[1] >= 9 and software_version < 14):
            print('Upgrade to version 11.14')

    return


