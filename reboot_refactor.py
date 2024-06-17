import os
from dotenv import load_dotenv
import time
import datetime
import sched
import requests
from openpyxl import load_workbook
import openpyxl
import concurrent.futures
import smtplib
import xml.etree.ElementTree as ET
from email.message import EmailMessage
from logger import log_info

#Loading Environment Variables
load_dotenv()
PASSCODE = os.environ.get("PASSCODE")
FILENAME = os.environ.get("FILENAME")
LOGPATH = os.environ.get("REBOOT_LOGPATH")

#Disable ssl warning
requests.packages.urllib3.disable_warnings()

#Creating custom exception
class CustomException(Exception):
    pass

#Combining logger and print statement
def message(string='', sys_name=''):
    print(string)
    log_info(string, sys_name, LOGPATH)

#Defining global headers
headers = {'Content-Type': 'text/xml', 'Authorization': f'basic {PASSCODE}'}


def get_sys_name(ip=''):
    try:
        xml = requests.get(f'http://{ip}/getxml?location=/Configuration/SystemUnit/Name', headers=headers, verify=False, timeout=(10, 30))
        print(xml.text)
        xml_root = ET.fromstring(xml.text)
        sys_name = xml_root[0][0].text
        return sys_name
    except requests.exceptions.HTTPError as err:
        message(err, ip)

def initiate_reboot(ip=''):
    sys_name = get_sys_name(ip)

    payload = '''<Command>
                    <Standby>
                        <Deactivate></Deactivate>
                    </Standby>
                    <UserInterface>
                        <Message>
                            <Alert>
                                <Display>
                                    <Duration>10</Duration>
                                    <Text>Use touchpanel to cancel reboot</Text>
                                    <Title>AUTOMATED REBOOT INITIATED</Title>
                                </Display>
                            </Alert>
                        </Message>
                    </UserInterface>
                </Command>'''

    try:
        response = requests.post( f'http://{ip}/putxml', headers=headers, verify=False, data=payload)
        message(response.text, sys_name)
        return response.text
    except requests.exceptions.HTTPError as err:
        message(err, sys_name)

if __name__ == '__main__':
    print(initiate_reboot('172.16.131.163'))