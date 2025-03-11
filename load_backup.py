import os
import subprocess
import requests
import xml.etree.ElementTree as ET
from time import sleep
from Utils.logger import log_info
from dotenv import load_dotenv
from Utils.select_backup import select_backup

load_dotenv()

environ = os.environ

BACKUP_SERVER_PATH = environ.get('BACKUP_SERVER_PATH')

class custom_exception(Exception):
    pass

#Removing insecure http warnings
requests.packages.urllib3.disable_warnings()

#Building Logger

def message(text, origin):
    print(f"{origin}: {text}")
    log_info(text, origin, LOGPATH)

#Loading environment variable
PASSCODE = environ.get('PASSCODE')
LOGPATH = environ.get('LOGPATH')
headers = {
    'Authorization': f'basic {PASSCODE}',
    'Content-Type': 'text/xml'
}
# BACKUP_FILE = environ.get('BACKUP_FILE')
# BACKUP_FILE_CHECKSUM = environ.get('BACKUP_FILE_CHECKSUM')

def fetch_backup_XML(file, checksum):
    string =f'''<Command>
            <Provisioning>
                <Service>
                    <Fetch>
                        <Checksum item="1" valueSpaceRef="/Valuespace/Vs_string_0_128">{checksum}</Checksum>
                        <URL item="1" valueSpaceRef="/Valuespace/Vs_string_0_2048">{BACKUP_SERVER_PATH}/{file}</URL>
                    </Fetch>
                </Service>
            </Provisioning>
        </Command>'''
    return string

def http_request(ip, string):
    try:
        response = requests.post(f'http://{ip}/putxml', headers=headers, verify=False, data=string, timeout=180)
        message(response.text, ip)
        return response.text
    except requests.exceptions.HTTPError as err:
        message(f'{ip} -> {err}', ip)

def get_sys_name(ip=''):
    try:
        xml = requests.get(f'http://{ip}/getxml?location=/Configuration/SystemUnit/Name', headers=headers, verify=False, timeout=(10, 30))
        print(xml.text)
        xml_root = ET.fromstring(xml.text)
        sys_name = xml_root[0][0].text
        return sys_name
    except requests.exceptions.HTTPError as err:
        print(err, ip)

def load_backup(codec, sup_file):
    #Getting device information
    sys_name = get_sys_name(codec.ip)
    
    #Fetching and loading backup
    backup_fetch_status = http_request(codec.ip, fetch_backup_XML(sup_file['filename'], sup_file['checksum']))
    message(f'{backup_fetch_status}', sys_name)
    
    if backup_fetch_status.find('<ServiceFetchResult status="OK">') != -1:
        message('Update Successful', sys_name)
        return f'{sys_name} - Changes made successfully'
    else:
        message(f'Could load backup for {sys_name}. Please investigate', sys_name)
        raise custom_exception(f'Could not load backup for {sys_name}. Please investigate.')

if __name__ == '__main__':
    backup_dict = select_backup()
    class Codec:
        def __init__(self, ip):
            self.name = 'One-Off Codec'
            self.ip = ip
    load_backup((Codec(input('Enter codec IP: '))), backup_dict)