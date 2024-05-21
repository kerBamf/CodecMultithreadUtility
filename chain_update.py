import os
from dotenv import load_dotenv
import time
import math
import requests
import xml.etree.ElementTree as ET


#Pulling Environment Variables
load_dotenv()

PASSCODE = os.environ.get('PASSCODE')
PROPATH = os.environ.get('PROPATH')
KITPATH = os.environ.get('KITPATH')

class UpgradeException(Exception):
    pass

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

#Checks software version. Used by chain_upgrade() command to determine where to start in the upgrade path. Returns a list of numbers where each list item pertains to a software version/sub-version.
def check_software(ip):
    headers = {'Authorization': f'basic {PASSCODE}'}
    
    try:
        soft_xml = requests.get(f'https://{ip}/getxml?location=/Status/SystemUnit/Software/Version', headers=headers, verify=False)
        xml_root = ET.fromstring(soft_xml.text)
        print(soft_xml.text)
        parsed_version = xml_root[0][0][0].text.replace('ce','').split('.')
        return parsed_version
    except requests.exceptions.HTTPError as err:
        print(err.response)
        return False


#Checks hardware version of the codec. Used to determine which upgrade file path to use. Returns a string of 'kit,' 'pro,' or 'SX80' 
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

#Function called when upgrade is initiated. Hardware version determines filepath, software version determines file to be used
def upgrade(hw_version, sw_version, ip):
    try:
        url = f'http://{ip}/putxml'
        headers = {'Authorization': 'basic YWRtaW46NzM2NjgzMjk='}
        payload = upgrade_command_xml(hw_version, sw_version)
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        print(response.text)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err.response)

    #Pinging codec after sending update command
    awake = True
    start = math.floor(time.time())
    time_passed = 0
    restarted = False
    while awake == True and time_passed < 60*10:
        ping = os.system(f"ping -c 1 {ip}")
        if (ping == 0):
            awake == True
            new_time = math.floor(time.time())
            time_passed = new_time - start
        else:
            awake = False
            restarted = True

    if (restarted == False):
        print('Codec upgrade failed. Please troubleshoot.')
        raise UpgradeException({'text':'Codec failed to pull update properly'})
        
    time.sleep(60 * 3)

    #Lost ping should mean codec restarted
    time_passed = 0
    start = math.floor(time.time())
    while awake == False and time_passed < 60*8:
        ping = os.system(f"ping -c 1 {ip}")
        if (ping == 0):
            awake == True
        else:
            awake == False
            new_time = math.floor(time.time())
            time_passed = start - new_time

    if (awake == False):
        raise UpgradeException({'text': 'Codec failed to restart. Please investigate'})
    
    return 'Upgrade complete'

#Command used to populate XML string to be sent to codec by upgrade command
def upgrade_command_xml(hw_version, sw_version):
    file_path = None
    if (hw_version == 'pro'):
        file_path = PROPATH
        file_string = pro_versions[sw_version]
    elif (hw_version == 'kit'):
        file_path = KITPATH
        file_string = kit_versions[sw_version]

    return f'<Command>\r\n\t<SystemUnit>\r\n\t\t<SoftwareUpgrade>\r\n\t\t\t<URL>{file_path}{file_string}</URL>\r\n\t\t</SoftwareUpgrade>\r\n\t</SystemUnit>\r\n</Command>'


# check_software('172.16.131.163')
def chain_update(ip):

    sw_version = check_software(ip) #Returns list of numbers for codec versions/sub-versions, or False for errors
    hw_version = check_hardware(ip) #Returns 'kit,' 'pro', or 'SX80', or False for errors

    #Exit conditions to cancel function should there be an error
    if (sw_version == False):
        raise UpgradeException({'text': 'Failed to retrive codec software version. Please investigate'})
    elif (hw_version == False):
        raise UpgradeException({'text': 'Failed to retrieve codec hardware version. Please investigate'
        })
    elif (hw_version == 'SX80'):
        raise UpgradeException({'text': 'Codec is an SX80. Script is only designed to work on newer systems'})

    # Returns chain update function if code is on the latest version. Changes will need to be added later to allow for dynamic edits to code versions as newer ones come out.
    if (sw_version[0] == 11 and sw_version[1] == 14):
        
        return 'Codec is running latest software. Exiting script'
    
    #Comparing code versions
    if (sw_version[0] < 10):
        if (sw_version[1] < 15):
            print('upgrade to version 9.15.3.22')
            try:
                upgrade(hw_version, '9.15', ip)
            except UpgradeException as err:
                print(err.text)
        else:
            print('Upgrade to version 10.15.4')
            try:
                upgrade(hw_version, '10.15', ip)
            except UpgradeException as err:
                print(err.text)
    elif (sw_version[0] == 10):
        if (sw_version[1] < 15):
            print('Upgrade to version 10.15.4')
            try:
                upgrade(hw_version, '10.15', ip)
            except UpgradeException as err:
                print(err.text)
        elif (sw_version[1] >= 15 and sw_version[1] < 19):
            print('Upgrade to version 10.19.4.2')
            try:
                upgrade(hw_version, '10.19', ip)
            except UpgradeException as err:
                print(err.text)
        else:
            print('Upgrade to version 11.5')
            try:
                upgrade(hw_version, '11.5', ip)
            except UpgradeException as err:
                print(err.text)
    elif (sw_version[0] == 11):
        if (sw_version[1] < 9 and hw_version):
            print('Upgrade to version 11.9')
            try:
                upgrade(hw_version, '11.9', ip)
            except UpgradeException as err:
                print(err.text)
        elif (sw_version[1] >= 9 and sw_version < 14):
            print('Upgrade to version 11.14')
            try:
                upgrade(hw_version, '11.14', ip)
            except UpgradeException as err:
                print(err.text)
    
    new_sw_version = check_software(ip)

    if (new_sw_version == sw_version):
        raise UpgradeException({'text': 'Codec restarted, but failed to update properly. Please investigate'})
    
    chain_update(ip)

    return 'Codec successfully upgraded'

chain_update('172.16.131.163')


