import os
import subprocess
import requests
import xml.etree.ElementTree as ET
from time import sleep
from Utils.logger import log_info
from Utils.select_backup import select_backup

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
BACKUP_SERVER_PASS = environ.get('BACKUP_SERVER_PATH')

# File XML to send via HTTP

set_transpile_XML = f'''<Configuration>
        <Macros>
            <EvaluateTranspiled>False</EvaluateTranspiled>
        </Macros>
    </Configuration>'''

def fetch_backup_XML(backup_dict):
    XML = f'''<Command>
        <Provisioning>
            <Service>
                <Fetch>
                    <Checksum item="1" valueSpaceRef="/Valuespace/Vs_string_0_128">{backup_dict['checksum']}</Checksum>
                    <URL item="1" valueSpaceRef="/Valuespace/Vs_string_0_2048">{BACKUP_SERVER_PASS+backup_dict['filename']}</URL>
                </Fetch>
            </Service>
        </Provisioning>
    </Command>'''

    return XML

def http_request(codec, string):
    try:
        response = requests.post(f'http://{codec.ip}/putxml', headers=headers, verify=False, data=string, timeout=180)
        log_info(response.text, codec.ip, LOGPATH)
        return response.text
    except requests.exceptions.HTTPError as err:
        log_info(f'{codec.ip} -> {err}', codec.ip, LOGPATH)

def new_codec_setup(codec, backup_dict):

    #Setting transpile to false
    set_transpile_status = http_request(codec.ip, set_transpile_XML)
    log_info(f'{set_transpile_status}', codec.ip, LOGPATH)
    
    
    #Fetching and loading backup
    backup_fetch_status = http_request(codec.ip, fetch_backup_XML(backup_dict))
    log_info(f'{backup_fetch_status}', codec.ip, LOGPATH)
    
    if backup_fetch_status.find('<p>The request could not be served due to a proxy error.</p>') != -1 or backup_fetch_status.find('<ServiceFetchResult status="OK">') != -1:
        log_info('Update Successful', codec.ip, LOGPATH)
        return f'{codec.ip} - Changes made successfully'
    else:
        log_info(f'Could not complete setup for {codec.ip}. Please investigate', codec.ip, LOGPATH)
        raise custom_exception(f'Could not complete setup for {codec.ip}. Please investigate.')


if __name__ == '__main__':
    backup_dict = select_backup()
    class Codec:
        def __init__(self, ip):
            self.name = 'One-Off Codec'
            self.ip = ip
    new_codec_setup(Codec(input('Enter Codec IP: ')), backup_dict)