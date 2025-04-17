import os
from dotenv import load_dotenv
import time
import math
import subprocess
import requests
import xml.etree.ElementTree as ET
from Utils.logger import log_info


#Pulling Environment Variables
load_dotenv()

PASSCODE = os.environ.get('PASSCODE')
PROPATH = os.environ.get('PROPATH')
KITPATH = os.environ.get('KITPATH')
TESTURL = os.environ.get('TESTURL')
LOGPATH = os.environ.get('LOGPATH')

all_sw_paths = {
    'kit': KITPATH,
    'pro': PROPATH
}

requests.packages.urllib3.disable_warnings()

class UpgradeException(Exception):
    pass

def message(string, sys_name):
    print(string)
    log_info(string, sys_name, LOGPATH)

# disable ssl warning, not currently working
# urllib3.disable_warnings(InsecureRequestWarning)

#Defining filenames to be appended to filepath in the upgrade_command_xml() function
all_sw_versions = {
    'kit': {
        '9.15': 'cmterm-s53200ce9_15_3_22.k3.cop.sgn',
        '10.15': 'cmterm-s53200ce10_15_4_1.k3.cop.sgn',
        '10.19': 'cmterm-s53200ce10_19_5_6.k3.cop.sgn',
        # '11.5': 'cmterm-s53200ce11_5_2_4.k4.cop.sha512',
        # '11.9': 'cmterm-s53200ce11_9_3_1.k4.cop.sha512',
        # '11.14': 'cmterm-s53200ce11_14_3_0.k4.cop.sha512',
        # '11.17': 'cmterm-s53200ce11_17_3_0.k4.cop.sha512',
        '11.20': 'cmterm-s53200ce11_20_2_3.k4.cop.sha512'
    },
    'pro': {
        '10.15': 'cmterm-s53300ce10_15_4_1.k3.cop.sgn',
        '10.19': 'cmterm-s53300ce10_19_5_6.k3.cop.sgn',
        # '11.5': 'cmterm-s53300ce11_5_4_6.k4.cop.sha512',
        # '11.9': 'cmterm-s53300ce11_9_3_1.k4.cop.sha512',
        # '11.14': 'cmterm-s53300ce11_14_2_3.k4.cop.sha512',
        # '11.17': 'cmterm-s53300ce11_17_3_0.k4.cop.sha512',
        '11.20': 'cmterm-s53300ce11_20_2_3.k4.cop.sha512'
    }
}
#Checks codec information and assigns hw_version tag for use by the upgrade function
def check_codec(codec):
    headers = {'Authorization': f'basic {PASSCODE}'}
    hardware_list = {
        'pro': ['Codec Pro', 'Room Bar', 'Room Bar Pro'],
        'kit': ['Room Kit', 'Room Kit Mini', 'Codec Plus', 'Room 55'],
        'SX80': 'SX80'
    }

    codec_info = {
        'sw_version': [],
        'hw_version': '',
        'sys_name': '',
        'sys_type': ''
    }
    #Retrieves name of codec
    try:
        xml = requests.get(f'https://{codec.ip}/getxml?location=/Configuration/SystemUnit/Name', headers=headers, verify=False, timeout=(10, 30))
        xml_root = ET.fromstring(xml.text)
        sys_name = xml_root[0][0].text
        codec_info['sys_name'] = sys_name
        message(f'Codec Name Found: {sys_name}', sys_name)
    except requests.RequestException as err:
        message(f'Error retrieving name of {codec.ip}', codec.name)
    
    #checks software version of the codec and splits the version info into a list for easier comparison in Upgrade function
    try:
        soft_xml = requests.get(f'https://{codec.ip}/getxml?location=/Status/SystemUnit/Software/Version', headers=headers, verify=False, timeout=(10, 30))
        xml_root = ET.fromstring(soft_xml.text)
        soft_text = xml_root[0][0][0].text
        codec_info['sw_version'] = soft_text.replace('ce','').split('.')
        message(f'Software found: {soft_text}', codec_info['sys_name'])
    except requests.RequestException as err:
        message(f'Error retrieving software version of {codec.ip}', codec.name)

    #Checks hardware version of the codec. Used to determine which upgrade file path to use. Returns a string of 'kit,' 'pro,' or 'SX80'   
    try:
        soft_xml = requests.get(f'http://{codec.ip}/getxml?location=/Status/SystemUnit/ProductPlatform', headers=headers, verify=False, timeout=(10, 30))
        xml_root = ET.fromstring(soft_xml.text)
        sys_type = xml_root[0][0].text
        codec_info['sys_type'] = sys_type
        if (sys_type == 'SX80'):
            codec_info['hw_version'] = 'SX80' 
        for unit in hardware_list['pro']:
            if (sys_type == unit):
                codec_info['hw_version'] = 'pro'
        for unit in hardware_list['kit']:
            if (sys_type == unit):
                codec_info['hw_version'] = 'kit'
        message(f'Hardware found: {sys_type}. Assigning hardware version: {codec_info["hw_version"]}', codec_info['sys_name'])

    except requests.RequestException as err:
        message(f'Error retrieving hardware version of {codec.name}', codec.name)
        raise err
    

    return codec_info


#Function called when upgrade is initiated. Hardware version determines filepath, software version determines file to be used
def upgrade(sys_name, current_sw, sw_path, sw_file, codec):
    message(f'Attempting to install {sw_file} on {sys_name}...', sys_name)
    try:
        url = f'http://{codec.ip}/putxml'
        headers = {'Authorization': f'basic {PASSCODE}'}
        payload = upgrade_command_xml(sw_path, sw_file)
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        print(response.text)
        xml_root = ET.fromstring(response.text)
        status = xml_root[0].attrib['status']
        if (status == 'OK'):
            message('Upgrade status OK. Proceeding.', sys_name)
        else:
            message(f'{codec.name} Upgrade status: {status}. {xml_root[0][0].text}. Attempted Software upgrade: {sw_file}', sys_name)
            raise UpgradeException({'text': f'{codec.name} Upgrade status: Error. {xml_root[0][0].text}. Attempted Software upgrade: {sw_file}'})
    except requests.exceptions.HTTPError as err:
        message(err.response, sys_name)


    def ping():
        return subprocess.run(["ping", "-c", "1", codec.ip], capture_output=True).returncode
    
    #Pinging codec after sending update command
    awake = True
    start = math.floor(time.time())
    time_passed = 0
    restarted = False
    message(f'Pinging {sys_name}...', sys_name)

    while awake and time_passed < 60*10:
        ping_var = ping()
        if (ping_var):
            awake = False
            restarted = True
            message(f'{sys_name} has shut down. Resuming ping in 1 minute.', sys_name)

        new_time = math.floor(time.time())
        time_passed = new_time - start
        if (time_passed % 10 == 0 and time_passed > 0):
            message(f'Still pinging {sys_name}', sys_name)
        time.sleep(1)

    if (restarted == False):
        message(f'{sys_name} upgrade failed. Please troubleshoot.')
        raise UpgradeException({'text':f'{sys_name} failed to pull update properly'})
        
    time.sleep(60)

    #Lost resuming ping after restart
    time_passed = 0
    start = math.floor(time.time())
    while awake == False and time_passed < 60*8:
        ping_var = ping()
        if ping_var == 0:
            awake = True
            message(f'{sys_name} has powered up, giving it a minute of breathing room.', sys_name)
        
        new_time = math.floor(time.time())
        time_passed = start - new_time
        if (time_passed % 10 == 0 and time_passed > 0):
            message(f'Still pinging {sys_name}', sys_name)
        time.sleep(1)

    if (awake == False):
        message(f'{sys_name} failed to restart. Please investigate', sys_name)
        raise UpgradeException({'text': f'{sys_name} failed to restart. Please investigate'})
    
    time.sleep(60)

    new_sw_version = check_codec(codec)['sw_version']

    if (new_sw_version == current_sw):
        message(f'{sys_name} restarted, but failed to update properly. Please investigate', sys_name)
        raise UpgradeException({'text': f'{sys_name} restarted, but failed to update properly. Please investigate'})
    
    confirmation = '.'.join(new_sw_version)

    message(f'********\r\n{confirmation} successfully installed on {sys_name}\r\n********', sys_name)

    return f'********\r\n{confirmation} successfully installed on {sys_name}\r\n********'


#Command used to populate XML string to be sent to codec by upgrade command
def upgrade_command_xml(file_path, file_string):

    return f'<Command>\r\n\t<SystemUnit>\r\n\t\t<SoftwareUpgrade>\r\n\t\t\t<URL>{file_path}{file_string}</URL>\r\n\t\t</SoftwareUpgrade>\r\n\t</SystemUnit>\r\n</Command>'


#Main command, iterates through available software versions and calls upgrade command as needed.
def quick_update(codec):

    codec_info = check_codec(codec)
    #Assigns software version upgrade list to use
    assigned_sw_list = all_sw_versions[codec_info['hw_version']]
    assigned_sw_keys = list(assigned_sw_list.keys())
    final_sw_version = assigned_sw_keys[len(assigned_sw_keys)-1].split('.')
    sys_name = codec_info['sys_name']

    #Assigns software file path to use
    assigned_sw_path = all_sw_paths[codec_info['hw_version']]

    # Returns chain update function if code is on the latest version. Changes will need to be added later to allow for dynamic edits to code versions as newer ones come out.
    if (int(codec_info['sw_version'][0]) >= int(final_sw_version[0]) and int(codec_info['sw_version'][1]) >= int(final_sw_version[1])):
        message(f'{codec_info["sys_name"]} running latest software. Exiting script.', sys_name)
        return f'{codec_info["sys_name"]} running latest software. Exiting script.'
    
    #Beginning upgrade iteration
    for key in assigned_sw_keys:
        cur_sw_version = codec_info['sw_version']
        split_key = key.split('.')
        if int(split_key[0]) == int(cur_sw_version[0]) and int(split_key[1]) > int(cur_sw_version[1]):
            try:
                upgrade(codec_info['sys_name'], cur_sw_version, assigned_sw_path, assigned_sw_list[key], codec)
            except UpgradeException as error:
                (except_dictionary) = error.args
                message(except_dictionary["text"], sys_name)
                #print(error['text'])
                raise error
        elif int(split_key[0]) > int(cur_sw_version[0]):
            try:
                upgrade(codec_info['sys_name'], cur_sw_version, assigned_sw_path, assigned_sw_list[key], codec)
            except UpgradeException as error:
                (except_dictionary) = error.args
                message(except_dictionary["text"], sys_name)
                #print(error['text'])
                raise error
    
    message(f'{codec_info["sys_name"]} successfully upgraded', sys_name)
    return {'Status': f'{codec_info["sys_name"]} successfully upgraded', 'ip': codec.ip}

if __name__ == '__main__':
    quick_update(input('Enter Codec IP: '))
