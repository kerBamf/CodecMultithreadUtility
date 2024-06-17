import os
from dotenv import load_dotenv
import time
import math
import datetime
import subprocess
import sched
import requests
from openpyxl import load_workbook
import openpyxl
import concurrent.futures
import smtplib
import xml.etree.ElementTree as ET
from email.message import EmailMessage
from logger import log_info
from codec_multithreader import iterator

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

#Base initiate reboot function
def initiate_reboot(ip='', sys_name=''):

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


#Reboot Process Function
def reboot_process(ip=''):
    sys_name = get_sys_name(ip)
    message(f'Systname name retrived: {sys_name}', sys_name)
    
    message('Initiating reboot...', sys_name)
    initiate_reboot(ip, sys_name)
    
    time.sleep(10) #Sleep accounting for alert delay before countdown begins

    message('Reboot initiated. Codec should reboot in 60 seconds', sys_name)

    time.sleep(45)

    def ping():
        return subprocess.run(["ping", "-c", "1", ip], capture_output=True).returncode

    #Pinging codec after sending reboot
    awake = True
    start = math.floor(time.time())
    time_passed = 0
    restarted = False
    message(f'Pinging {sys_name} to confirm shutdown...', sys_name)

    while awake and time_passed < 60:
        ping_var = ping()
        if (ping_var):
            awake = False
            restarted = True
            message(f'{sys_name} has shut down. Resuming ping in 1 minute.', sys_name)

        new_time = math.floor(time.time())
        time_passed = new_time - start
        if (time_passed % 10 == 0 and time_passed > 0):
            message(f'Still pinging {sys_name}', sys_name)
        time.sleep(1)

    if restarted == False:
        message('Codec did not reboot. Please investigate', sys_name)
        raise CustomException(f'{sys_name} did not restart. Please investigate')
    
    time.sleep(60)

    #Resuming ping after restart to confirm codec has rebooted
    time_passed = 0
    start = math.floor(time.time())
    while awake == False and time_passed < 60*8:
        ping_var = ping()
        if ping_var == 0:
            awake = True
            message(f'{sys_name} has powered up.', sys_name)
        
        new_time = math.floor(time.time())
        time_passed = start - new_time
        if (time_passed % 10 == 0 and time_passed > 0):
            message(f'Still pinging {sys_name}', sys_name)
        time.sleep(1)

    if (awake == False):
        message(f'{sys_name} failed to restart. Please investigate', sys_name)
        raise CustomException(f'{sys_name} failed to restart. Please investigate')
    
    message(f'{sys_name} reboot successful', sys_name)
    return f'{sys_name} reboot successful'
    
# Using iterator to multithread over all IPs in a given list


if __name__ == '__main__':
    reboot_process('172.16.131.163')