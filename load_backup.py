import os
import subprocess
import requests
import xml.etree.ElementTree as ET
from time import sleep
from logger import log_info

environ = os.environ

class custom_exception(Exception):
    pass

#Removing insecure http warnings
requests.packages.urllib3.disable_warnings()

#Loading environment variable
PASSCODE = environ.get('PASSCODE')
LOGPATH = environ.get('LOGPATH')
headers = {
    'Authorization': f'basic {PASSCODE}',
    'Content-Type': 'text/xml'
}
BACKUP_FILE = environ.get('BACKUP_FILE')
BACKUP_FILE_CHECKSUM = environ.get('BACKUP_FILE_CHECKSUM')

fetch_backup_XML = f'''<Command>
    <Provisioning>
        <Service>
            <Fetch>
                <Checksum item="1" valueSpaceRef="/Valuespace/Vs_string_0_128">{BACKUP_FILE_CHECKSUM}</Checksum>
                <URL item="1" valueSpaceRef="/Valuespace/Vs_string_0_2048">{BACKUP_FILE}</URL>
            </Fetch>
        </Service>
    </Provisioning>
</Command>'''

def http_request(ip, string):
    try:
        response = requests.post(f'http://{ip}/putxml', headers=headers, verify=False, data=string, timeout=180)
        log_info(response.text, ip, LOGPATH)
        return response.text
    except requests.exceptions.HTTPError as err:
        log_info(f'{ip} -> {err}', ip, LOGPATH)

def get_sys_name(ip=''):
    try:
        xml = requests.get(f'http://{ip}/getxml?location=/Configuration/SystemUnit/Name', headers=headers, verify=False, timeout=(10, 30))
        print(xml.text)
        xml_root = ET.fromstring(xml.text)
        sys_name = xml_root[0][0].text
        return sys_name
    except requests.exceptions.HTTPError as err:
        print(err, ip)

def load_backup(ip):
    #Getting device information
    sys_name = get_sys_name(ip)
    
    #Fetching and loading backup
    backup_fetch_status = http_request(ip, fetch_backup_XML)
    log_info(f'{backup_fetch_status}', sys_name, LOGPATH)
    
    if backup_fetch_status.find('<ServiceFetchResult status="OK">') != -1:
        log_info('Update Successful', sys_name, LOGPATH)
        return f'{sys_name} - Changes made successfully'
    else:
        log_info(f'Could not complete consolidation for {sys_name}. Please investigate', sys_name, LOGPATH)
        raise custom_exception(f'Could not complete consolidation for {sys_name}. Please investigate.')


if __name__ == '__main__':
    load_backup(input('Enter Codec Ip: '))