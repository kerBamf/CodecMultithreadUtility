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

#Setting up logger
def message(string, ip, path=LOGPATH):
    log_info(string, ip, path)
    print(string)

def http_request(codec, string):
    try:
        response = requests.post(f'http://{codec.ip}/putxml', headers=headers, verify=False, data=string, timeout=60)
        message(f'Command Response: {response.text}', codec.name)
    except requests.exceptions.HTTPError as err:
        message(f'{codec.name} -> {err}', codec.name)
    return response

def send_command(codec, xml):
    response = http_request(codec, xml)
    return response.text

if __name__ == '__main__':
    new_XML = xml_selector()
    class Codec:
        def __init__(self, ip):
            self.name = 'One-Off Codec'
            self.ip = ip
    send_command(Codec(input('Enter codec IP: ')), new_XML)