from os import environ
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
from time import sleep
from Utils.logger import log_info
from Utils.xml_selector import xml_selector
from Utils.cod_get import cod_get
import xml.etree.ElementTree as ET

#Loading environment variable
load_dotenv()
PASSCODE = environ.get('PASSCODE')
LOGPATH = environ.get('LOGPATH')
headers = {
    'Authorization': f'basic {PASSCODE}'
}

#Setting up logger
def message(string, ip, path=LOGPATH):
    log_info(string, ip, path)
    print(string)

#Get Codec Name
def get_sys_name(ip=''):
    xml = cod_get(ip ,"Configuration/SystemUnit/Name")
    xml_root = ET.fromstring(xml)
    sys_name = xml_root[0][0].text
    return sys_name


def get_info(ip, path):
    sys_name = get_sys_name(ip)
    response = cod_get(ip, path)
    res_dict = {
        'name': sys_name,
        'response': response
    }
    message(res_dict, ip)
    return res_dict

if __name__ == '__main__':
    cod_IP = input("Enter Codec IP: ")
    info_path = input("Enter path string: ")
    get_info(cod_IP, info_path)