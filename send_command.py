from os import environ
import requests
import xml.etree.ElementTree as ET
from time import sleep
from Utils.logger import log_info
from Utils.xml_selector import xml_selector

#Removing insecure http warnings
requests.packages.urllib3.disable_warnings()

#Loading environment variable
PASSCODE = environ.get('PASSCODE')
LOGPATH = environ.get('LOGPATH')
headers = {
    'Authorization': f'basic {PASSCODE}',
    'Content-Type': 'text/xml'
}

new_XML = xml_selector()

#Setting up logger
def message(string, ip, path=LOGPATH):
    log_info(string, ip, path)
    print(string)

def http_request(ip, string):
    try:
        response = requests.post(f'http://{ip}/putxml', headers=headers, verify=False, data=string, timeout=60)
        message(f'Command Response: {response.text}', ip)
    except requests.exceptions.HTTPError as err:
        message(f'{ip} -> {err}', ip)
    return response

def send_command(ip, xml):
    response = http_request(ip, xml)
    return response.text

if __name__ == '__main__':
    send_command(input('Enter Codec IP: '), new_XML)