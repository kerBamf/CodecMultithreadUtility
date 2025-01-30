import xml.etree.ElementTree as ET
import datetime
import os
import subprocess
import requests
import json
from dotenv import load_dotenv
from Utils.logger import log_info

#Disable ssl warning
requests.packages.urllib3.disable_warnings()

#Loading environment variables
load_dotenv()
SAVE_PATH = os.environ.get('BACKUP_SAVE_PATH')
PASSCODE = os.environ.get('PASSCODE')
LOGPATH = os.environ.get('LOGPATH')

#Setting up custom exception

class custom_exception(Exception):
    pass

#Setting up logger
def message(string='', sys_name=''):
    print(string)
    log_info(string, sys_name, LOGPATH)

#Setting up headers for HTTP requests:
headers = {'Content-Type': 'text/xml', 'Authorization': f'basic {PASSCODE}'}

#Function retrieving codec system name for logging purposes
def get_sys_name(ip=''):
    try:
        xml = requests.get(f'http://{ip}/getxml?location=/Configuration/SystemUnit/Name', headers=headers, verify=False, timeout=(10, 30))
        print(xml.text)
        xml_root = ET.fromstring(xml.text)
        sys_name = xml_root[0][0].text
        return sys_name
    except requests.exceptions.HTTPError as err:
        message(err, ip)

#Function retrieving codec configration to be parsed
def get_sys_config(ip=''):
    try:
        xml = requests.get(f'http://{ip}/getxml?location=/Configuration', headers=headers, verify=False, timeout=(10, 30))
        xml_root = ET.fromstring(xml.text)
        return xml_root
    except requests.exceptions.HTTPError as err:
        message(err, ip)

#Getting Date for use by multiple functions
today = datetime.datetime.now().strftime('%x').replace('/', '-')


#Checks to see if directory and backup file already exists, and deletes it if it does. This ensures that redundant configurations won't be saved to the same file.
def check_backup_file(sys_name='', save_path=''):
    day_directory = f'{save_path}/Backup_Date_{today}'
    sys_directory = f'{save_path}/Backup_Date_{today}/{sys_name}_{today}'
    if not os.path.isdir(day_directory):
        subprocess.run(['mkdir', f'{day_directory}'], capture_output=True)
    if not os.path.isdir(sys_directory):
        subprocess.run(['mkdir', f'{sys_directory}'], capture_output=True)
    filename = 'configuration.txt'
    if os.path.isfile(f'{sys_directory}/{filename}'):
        subprocess.run(['rm', f'{sys_directory}/{filename}'])
        message('Old backup deleted.', sys_name)


#Appends strings to new backup file as a line of text
def append_file(string='', sys_name='', directory=''):
    filename = 'configuration.txt'

    with open(f"{directory}/{filename}", "a", newline='') as file:
        file.write(f'{string}\n')
     
    return filename

#Recursive XML parsing algorithm converting XML config to .txt file. As each node is visited, the string to be added to the .txt file is built node by node
def parse_xml(root, string='', sys_name='', directory=''):
    if string == '':
        string = root.tag
    elif root.attrib and len(root.attrib) > 1:
        string = f'{string} {root.tag} {root.attrib["item"]}'
    else:
        string = f'{string} {root.tag}'
    
    #Checks for child nodes, recursively calling function if they exist, passing the partially built string with it
    if len(root) >= 1: 
        for child in root:
            parse_xml(child, string, sys_name, directory)

    #Once the full path of an attribute is reached (the end of a branch in the XML tree), the string is completed and the line appended to the .txt file. Necessary string modifiers for edge cases are in place here to ensure proper syntax in the .txt file.
    else: 
        if 'Name' in root.tag: 
            string = f'{string}: "{root.text}"'
        else:
            string = f'{string}: {root.text}'
        string = string.replace('Configuration', '').replace('None', '""').replace('""""', '""')
        if root.tag == 'Parity':
            string = string.replace('""', 'None')
        append_file(string, sys_name, directory)

        #Once the line has been appended to the .txt file, the attributes and values of the current node are removed, allowing the string to be reused by the previously called function
        string = string.replace(f': {root.text}', '') 
        string = string.replace(f' {root.tag}', '')
        if root.attrib and len(root.attrib) > 1:
            string = string.replace(f' {root.attrib["item"]}', '')
        return

#Generates manifest, deleting old one if it already exists.
def generate_manifest(sys_name='', directory=''):
    now = datetime.datetime.now().strftime('%X')
    manifest = {
        "version": "1",
        "profile": {
            "configuration": {
            "items": [
                {
                "payload": 'configuration.txt',
                "type": "zip",
                "id": "_singleton"
                }
            ]
            }
        },
        "profileName": f"{sys_name}-{now}",
        "generatedAt": f"{now}"
    }
    if os.path.isfile(f'{directory}/manifest.json'):
        subprocess.run(['rm', f'{directory}/manifest.json'])
    with open(f"{directory}/manifest.json", "a", newline='') as file:
        json.dump(manifest, file, indent=2)


#Function compressing generated manifest and configuration file into a .zip folder

def compress_zip(directory='', sys_name=''):
    filename = f'{sys_name}_{today}.zip'
    if os.path.isfile(f'{directory}/{filename}'):
        subprocess.run(['rm', f'{directory}/{sys_name}_{today}_backup.zip'], capture_output=True)
    subprocess.run(['zip', f'{directory}/{sys_name}_{today}_backup.zip', f'{directory}/configuration.txt', f'{directory}/manifest.json'], capture_output=True)

#Function generating a sha512 checksum for use by remote backup restoration commands
def generate_checksum(directory='', sys_name=''):
    backup_file = f'{directory}/{sys_name}_{today}_backup.zip'
    filename = 'sha512_checksum.txt'
    if os.path.isfile(f'{directory}/{filename}'):
        subprocess.run(['rm', f'{directory}/{filename}'], capture_output=True)
    raw_checksum = subprocess.run(['shasum', '-a', '512', f'{backup_file}'], capture_output=True, text=True)
    if raw_checksum.stderr == '':
        string = raw_checksum.stdout.split(' ')[0]
    else:
        raise custom_exception(raw_checksum.stderr)
    
    print(string)
    with open(f'{directory}/{filename}', 'a', newline='') as file:
        file.write(f'{string}')

#Main function
def backup_utility(ip):
    sys_name = get_sys_name(ip)
    directory = f'{SAVE_PATH}/Backup_Date_{today}/{sys_name}_{today}'
    message(f'System name retrieved: {sys_name}\r\nPulling system backup...', sys_name)
    config_xml = get_sys_config(ip)
    message('Configuration file retrieved', sys_name)
    message('Checking directory and filename...', sys_name)
    check_backup_file(sys_name, SAVE_PATH)
    message('Parsing XML...', sys_name)
    parse_xml(config_xml, '', sys_name, directory)
    message('Generating manifest', sys_name)
    generate_manifest(sys_name, directory)
    message('Compressing files...', sys_name)
    compress_zip(directory, sys_name)
    generate_checksum(directory, sys_name)
    message('Backup completed', sys_name)
    resolution = {
        'Status': 'Backup Completed',
        'System_name': sys_name
    }
    return resolution

if __name__ == '__main__':
    backup_utility(input('Enter codec IP: '))