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
FILE = environ.get('SETUP_FILE')
CHECKSUM = environ.get('SETUP_FILE_CHECKSUM')

# File XML to send via HTTP

set_transpile_XML = f'''<Configuration>
        <Macros>
            <EvaluateTranspiled>False</EvaluateTranspiled>
        </Macros>
    </Configuration>'''

fetch_backup_XML = f'''<Command>
    <Provisioning>
        <Service>
            <Fetch>
                <Checksum item="1" valueSpaceRef="/Valuespace/Vs_string_0_128">{CHECKSUM}</Checksum>
                <URL item="1" valueSpaceRef="/Valuespace/Vs_string_0_2048">{FILE}</URL>
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

def new_codec_setup(ip):

    #Setting transpile to false
    set_transpile_status = http_request(ip, set_transpile_XML)
    log_info(f'{set_transpile_status}', ip, LOGPATH)
    
    
    #Fetching and loading backup
    backup_fetch_status = http_request(ip, fetch_backup_XML)
    log_info(f'{backup_fetch_status}', ip, LOGPATH)
    
    if backup_fetch_status.find('<p>The request could not be served due to a proxy error.</p>') != -1 or backup_fetch_status.find('<ServiceFetchResult status="OK">') != -1:
        log_info('Update Successful', ip, LOGPATH)
        return f'{ip} - Changes made successfully'
    else:
        log_info(f'Could not complete setup for {ip}. Please investigate', ip, LOGPATH)
        raise custom_exception(f'Could not complete setup for {ip}. Please investigate.')


if __name__ == '__main__':
    new_codec_setup(input('Enter Codec Ip: '))