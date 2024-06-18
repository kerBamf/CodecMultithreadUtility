import xml.etree.ElementTree as ET
import datetime
import os
import subprocess
import requests
from logger import log_info


#TO DO: make sure code can be run by multithreader with correct logging
#Add request function to retrieve XML from remote codec
#Add zipping functionality to make backup ready for


#Disable ssl warning
requests.packages.urllib3.disable_warnings()

#Loading environment variables
SAVE_PATH = os.environ.get('BACKUP_PATH')
PASSCODE = os.environ.get('PASSCODE')

#Setting up logger
def message(string='', sys_name=''):
    print(string)
    log_info(string, sys_name, SAVE_PATH)

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

#Checks defined backup directory for a folder with the current date. if one does not exist, it creates a new directory for backups pulled that day
# def check_backup_dir(path='', date=''):
#     if not os.path.isdir(f'{path}/BackupDate_{date}'):
#         subprocess.run(['mkdir', f'{path}/BackupDate_{date}'], capture_output=True)
#         return f'/BackupDate_{date}'
#     else:
#         return f'/BackupDate_{date}'

#Checks to see if directory and backup file already exists, and deletes it if it does. This ensures that redundant configurations won't be saved to the same file.
def check_backup_file(sys_name='', save_path=''):
    today = datetime.datetime.now().strftime('%x').replace('/', '-')
    directory = f'{save_path}/BackupDate_{today}'
    if not os.path.isdir(directory):
        subprocess.run(['mkdir', f'{directory}'], capture_output=True)
    filename = f'{sys_name}_backup_{today}.txt'
    if os.path.isfile(f'{directory}/{filename}'):
        subprocess.run(['rm', f'{directory}/{filename}'])
        message('Old backup deleted.', sys_name)


#Appends configuration lines to new backup file
def append_file(string='', sys_name='', save_path=''):
    today = datetime.datetime.now().strftime('%x').replace('/', '-')
    now = datetime.datetime.now().strftime('%X')
    timestamp = f'{today}_{now}'
    filename = f'{sys_name}_backup_{today}.txt'
    directory = f'{save_path}/BackupDate_{today}'

    with open(f"{directory}/{filename}", "a", newline='') as file:
        file.write(f'{string}\n')
     
    return timestamp

#Recursive XML parsing algorithm printing to .txt file.
def parse_xml(root, string='', sys_name=''):
    if string == '':
        string = root.tag
    elif root.attrib and len(root.attrib) > 1:
        string = f'{string} {root.tag} {root.attrib['item']}'
    else:
        string = f'{string} {root.tag}'
    if len(root) >= 1:
        for child in root:
            parse_xml(child, string, sys_name)
    else:
        if 'Name' in root.tag: 
            string = f'{string}: "{root.text}"'
        else:
            string = f'{string}: {root.text}'
        string = string.replace('Configuration', '').replace('None', '""').replace('""""', '""')
        if root.tag == 'Parity':
            string = string.replace('""', 'None')
        append_file(string, f'{sys_name}', SAVE_PATH)
        string = string.replace(f': {root.text}', '')
        string = string.replace(f' {root.tag}', '')
        if root.attrib and len(root.attrib) > 1:
            string = string.replace(f' {root.attrib['item']}', '')
        return

#Main function
def backup_utility(ip):
    sys_name = get_sys_name(ip)
    message('System name retrieved', sys_name)
    config_xml = get_sys_config(ip)
    message('Configuration file retrieved', sys_name)
    message('Checking directory and filename...', sys_name)
    check_backup_file(sys_name, SAVE_PATH)
    message('Parsing XML...', sys_name)
    parse_xml(config_xml, '', sys_name)
    message('Backup completed', sys_name)

if __name__ == '__main__':
    backup_utility('172.16.131.163')