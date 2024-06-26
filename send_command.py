from os import environ
import requests
import xml.etree.ElementTree as ET
from time import sleep
from logger import log_info

#Removing insecure http warnings
requests.packages.urllib3.disable_warnings()

#Loading environment variable
PASSCODE = environ.get('PASSCODE')
LOGPATH = environ.get('LOGPATH')
headers = {
    'Authorization': f'basic {PASSCODE}',
    'Content-Type': 'text/xml'
}

refresh_XML = '''<Configuration>
    <UserInterface>
        <Features>
            <Call>
                <Webcam>Hidden</Webcam>
            </Call>
        </Features>
    </UserInterface>
</Configuration>'''

def http_request(ip, string):
    try:
        response = requests.post(f'http://{ip}/putxml', headers=headers, verify=False, data=string, timeout=60)
        log_info(f'Halfwake command: {response.text}', ip, LOGPATH)
    except requests.exceptions.HTTPError as err:
        log_info(f'{ip} -> {err}', ip, LOGPATH)

def send_command(ip):
    response = http_request(ip, refresh_XML)
    return response.text

if __name__ == '__main__':
    send_command(input('Enter Codec IP: '))