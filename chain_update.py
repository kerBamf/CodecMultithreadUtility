import os
from dotenv import load_dotenv
import time
import math
import subprocess
import requests
import xml.etree.ElementTree as ET


#Pulling Environment Variables
load_dotenv()

PASSCODE = os.environ.get('PASSCODE')
PROPATH = os.environ.get('PROPATH')
KITPATH = os.environ.get('KITPATH')

requests.packages.urllib3.disable_warnings()

class UpgradeException(Exception):
    pass

# disable ssl warning, not currently working
# urllib3.disable_warnings(InsecureRequestWarning)

#Defining filenames to be appended to filepath in the upgrade_command_xml() function
kit_versions = {
    '9.15': 'cmterm-s53200ce9_15_3_22.k3.cop.sgn',
    '10.19': 'cmterm-s53200ce10_19_5_6.k3.cop.sgn',
    '10.15': 'cmterm-s53200ce10_15_4_1.k3.cop.sgn',
    '11.5': 'cmterm-s53200ce11_5_2_4.k4.cop.sha512',
    '11.9': 'cmterm-s53200ce11_9_3_1.k4.cop.sha512',
    '11.14': 'cmterm-s53200ce11_14_2_3.k4.cop.sha512'
}

pro_versions = {
    '10.15': 'cmterm-s53300ce10_15_4_1.k3.cop.sgn', 
    '10.19': 'cmterm-s53300ce10_19_5_6.k3.cop.sgn',
    '11.5': 'cmterm-s53300ce11_5_4_6.k4.cop.sha512',
    '11.9': 'cmterm-s53300ce11_9_3_1.k4.cop.sha512',
    '11.14': 'cmterm-s53300ce11_14_2_3.k4.cop.sha512',
}

#Checks software version. Used by chain_upgrade() command to determine where to start in the upgrade path. Returns a list of numbers where each list item pertains to a software version/sub-version.
def check_software(ip):
    headers = {'Authorization': f'basic {PASSCODE}'}
    
    try:
        soft_xml = requests.get(f'https://{ip}/getxml?location=/Status/SystemUnit/Software/Version', headers=headers, verify=False)
        xml_root = ET.fromstring(soft_xml.text)
        soft_text = xml_root[0][0][0].text
        split_version = soft_text.replace('ce','').split('.')
        print(f'Software found: {soft_text}')
        return split_version
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
        xml_root = ET.fromstring(soft_xml.text)
        parsed_version = xml_root[0][0].text
        print(f'Hardware found: {parsed_version}')
        if (parsed_version == 'SX80'):
            return 'SX80'
        for unit in hardware_list['pro']:
            if (parsed_version == unit):
                return 'pro'
        for unit in hardware_list['kit']:
            if (parsed_version == unit):
                return 'kit'

    except requests.exceptions.HTTPError as err:
        print(err.response)
        return False
    
def check_system_name(ip):
    headers = {'Authorization': f'basic {PASSCODE}'}

    try:
        xml = requests.get(f'https://{ip}/getxml?location=/Configuration/SystemUnit/Name', headers=headers, verify=False)
        xml_root = ET.fromstring(xml.text)
        system_name = xml_root[0][0].text
        print(f'Codec Name Found: {system_name}')
        return system_name
    except requests.exceptions.HTTPError as err:
        print(err.response)
        return False

#Function called when upgrade is initiated. Hardware version determines filepath, software version determines file to be used
def upgrade(sys_name, hw_version, sw_version, ip):

    try:
        url = f'http://{ip}/putxml'
        headers = {'Authorization': 'basic YWRtaW46NzM2NjgzMjk='}
        payload = upgrade_command_xml(hw_version, sw_version)
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        xml_root = ET.fromstring(response.text)
        status = xml_root[0].attrib['status']
        if (status == 'OK'):
            print('Upgrade status OK. Proceeding.')
        else:
            print(f'Upgrade status: {status}. {xml_root[0].text}')
            raise UpgradeException({'text': f'Upgrade status: Error. {xml_root[0].text}'})
    except requests.exceptions.HTTPError as err:
        print(err.response)

    #Pinging codec after sending update command
    awake = True
    start = math.floor(time.time())
    time_passed = 0
    restarted = False
    print(f'Pinging {sys_name}...')
    while awake == True and time_passed < 60*10:
        ping = subprocess.run(["ping", "-c", "1", ip], capture_output=True).returncode
        if (ping == 0):
            awake = True
            new_time = math.floor(time.time())
            time_passed = new_time - start
            if (time_passed % 10 == 0 and time_passed > 0):
                print(f'Still pinging {sys_name}')
            time.sleep(1)
        else:
            awake = False
            restarted = True
            print(f'{sys_name} has shut down. Resuming ping in 1 minute.')

    if (restarted == False):
        print(f'{sys_name} upgrade failed. Please troubleshoot.')
        raise UpgradeException({'text':f'{sys_name} failed to pull update properly'})
        
    time.sleep(60)

    #Lost ping should mean codec restarted
    time_passed = 0
    start = math.floor(time.time())
    while awake == False and time_passed < 60*8:
        ping = subprocess.run(["ping", "-c", "1", ip], capture_output=True).returncode
        if (ping == 0):
            awake = True
            print(f'{sys_name} has powered up, giving it a minute of breathing room.')
        else:
            awake = False
            new_time = math.floor(time.time())
            time_passed = start - new_time
            if (time_passed % 10 == 0 and time_passed > 0):
                print(f'Still pinging {sys_name}')
            time.sleep(1)

    if (awake == False):
        print(f'{sys_name} failed to restart. Please investigate')
        raise UpgradeException({f'text': f'{sys_name} failed to restart. Please investigate'})
    
    time.sleep(60)

    return f'Upgrade complete on {sys_name}'

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
def step_update(ip):

    hw_version = check_hardware(ip) #Returns 'kit,' 'pro', or 'SX80', or False for errors
    sw_version = check_software(ip) #Returns list of numbers for codec versions/sub-versions, or False for errors
    sys_name = check_system_name(ip)

    #Exit conditions to cancel function should there be an error
    if (sw_version == False):
        raise UpgradeException({'text': 'Failed to retrive codec software version. Please investigate'})
    elif (hw_version == False):
        raise UpgradeException({'text': 'Failed to retrieve codec hardware version. Please investigate'
        })
    elif (hw_version == 'SX80'):
        raise UpgradeException({'text': 'Codec is an SX80. Script is only designed to work on newer systems'})

    # Returns chain update function if code is on the latest version. Changes will need to be added later to allow for dynamic edits to code versions as newer ones come out.
    if (int(sw_version[0]) == 11 and int(sw_version[1]) == 14):
        # print(f'{sys_name} is runnnig latest software. Exiting script')
        return f'{sys_name} running latest software. Exiting script'
    
    #Comparing code versions
    if (int(sw_version[0]) < 10):
        if (int(sw_version[1]) < 15):
            print('upgrade to version 9.15.3.22')
            try:
                upgrade(sys_name, hw_version, '9.15', ip)
            except UpgradeException as err:
                print(err.text)
        else:
            print('Upgrade to version 10.15.4')
            try:
                upgrade(sys_name, hw_version, '10.15', ip)
            except UpgradeException as err:
                print(err.text)
    elif (int(sw_version[0]) == 10):
        if (int(sw_version[1]) < 15):
            print('Upgrade to version 10.15.4')
            try:
                upgrade(sys_name, hw_version, '10.15', ip)
            except UpgradeException as err:
                print(err.text)
        elif (int(sw_version[1]) >= 15 and int(sw_version[1]) < 19):
            print('Upgrade to version 10.19.4.2')
            try:
                upgrade(sys_name, hw_version, '10.19', ip)
            except UpgradeException as err:
                print(err.text)
        elif (int(sw_version[1]) == 19):
            print('Upgrade to version 11.5')
            try:
                upgrade(sys_name, hw_version, '11.5', ip)
            except UpgradeException as err:
                print(err.text)
    elif (int(sw_version[0]) == 11):
        if (int(sw_version[1]) < 9):
            print('Upgrade to version 11.9')
            try:
                upgrade(sys_name, hw_version, '11.9', ip)
            except UpgradeException as err:
                print(err.text)
        elif (int(sw_version[1]) >= 9 and int(sw_version[1]) < 14):
            print('Upgrade to version 11.14')
            try:
                upgrade(sys_name, hw_version, '11.14', ip)
            except UpgradeException as err:
                print(err.text)
    
    new_sw_version = check_software(ip)

    if (new_sw_version == sw_version):
        print(f'{sys_name} restarted, but failed to update properly. Please investigate')
        raise UpgradeException({'text': f'{sys_name} restarted, but failed to update properly. Please investigate'})
    
    confirmation = '.'.join(new_sw_version)
    
    print(f'********\r\n{confirmation} successfully installed on {sys_name}\r\n********')

    step_update(ip)

    return f'{sys_name} successfully upgraded'

if __name__ == '__main__':
    step_update('172.16.131.191')


