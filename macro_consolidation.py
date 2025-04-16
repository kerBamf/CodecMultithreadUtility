import os
import subprocess
import requests
import xml.etree.ElementTree as ET
from time import sleep
from Utils.logger import log_info
from Utils.select_backup import select_backup
from Utils.cod_post import cod_session_start, cod_session_end, cod_post
from Utils.cod_get import cod_get
import json
from dotenv import load_dotenv
from dataclasses import dataclass

# Loading environment variables
load_dotenv()
environ = os.environ

# Setting up custom exception class
class custom_exception(Exception):
    pass

#Removing insecure http warnings
requests.packages.urllib3.disable_warnings()

#Loading environment variable
PASSCODE = environ.get('PASSCODE')
LOGPATH = environ.get('LOGPATH')
BACKUP_SERVER_PATH = environ.get('BACKUP_SERVER_PATH')

#Logger
def message(string, device):
    print(string)
    log_info(string, device, LOGPATH)

# Listing all macros to remove for loop iteration
macros_to_remove = [
    'Nightly_Reboot',
    'Check_Standby',
    'External_reset',
    'TeamsDialler',
    'ZoomDialler',
    'InstructionsPanel'
]

def get_rm_macro_string(name):
    string = f'''<Body>
            <Command>
                <Macros>
                    <Macro>
                        <Remove>
                            <Name>{name}</Name>
                        </Remove>
                    </Macro>
                </Macros>
            </Command>
        </Body>'''
    return string

UIs_to_remove = [
    'instructions',
    'closeInstructionsHome'
]

# Listing all UI elements to remove for loop iteration
def get_rm_UI_string(name):
    string = f'''<Body>
        <Command>
            <UserInterface>
                <Extensions>
                    <Panel>
                        <Remove>
                            <PanelId>{name}</PanelId>
                        </Remove>
                    </Panel>
                </Extensions>
            </UserInterface>
        </Command>
    </Body>'''
    return string


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

set_transpile_XML = f'''<Configuration>
        <Macros>
            <EvaluateTranspiled>False</EvaluateTranspiled>
        </Macros>
    </Configuration>'''

# def http_request(ip, string):
#     try:
#         response = requests.post(f'http://{ip}/putxml', headers=headers, verify=False, data=string, timeout=180)
#         message(response.text, ip)
#         return response.text
#     except requests.exceptions.HTTPError as err:
#         message(f'{ip} -> {err}', ip)

def get_sys_name(codec):
    try:
        xml = cod_get(codec.ip, 'Configuration/SystemUnit/Name')
        message(xml, codec.name)
        xml_root = ET.fromstring(xml)
        sys_name = xml_root[0][0].text
        return sys_name
    except requests.exceptions.HTTPError as err:
        message(err, codec.name)

def config_consolidation(codec, sup_file):
    try:
        #Getting device information
        sys_name = get_sys_name(codec)

        #Begin Session
        cookie = cod_session_start(codec.ip)

        #Removing macros
        for macro in macros_to_remove:
            cod_post(codec.ip, get_rm_macro_string(macro), cookie)
            message(f'Removing {macro}...', sys_name)
        
        #removing UI elements
        for ui in UIs_to_remove:
            cod_post(codec.ip, get_rm_UI_string(ui), cookie)
            message(f'Removing {ui}...', sys_name)
        
        #setting EvaluateTranspiled to False
        set_transpile_status = cod_post(codec.ip, set_transpile_XML, cookie)
        message(f'Transpile status: {set_transpile_status}', sys_name)

        #Fetching and loading backup
        backup_fetch_status = cod_post(codec.ip, fetch_backup_XML(sup_file['filename'], sup_file['checksum']), cookie)
        message(f'Backup status: {backup_fetch_status}', sys_name)
        
        if backup_fetch_status.find('<ServiceFetchResult status="OK">') != -1:
            message('Update Successful', sys_name)
            cod_session_end(codec.ip, cookie)
            return f'{sys_name} - Changes made successfully'
        else:
            message(f'Could not complete consolidation for {sys_name}. Please investigate', sys_name)
            raise custom_exception(f'Could not complete consolidation for {sys_name}. Please investigate.')
    except custom_exception as err:
        message(err, codec.name)
        cod_session_end(codec.ip, cookie)




if __name__ == '__main__':
    backup_dict = select_backup()
    class Codec:
        def __init__(self, ip):
            self.name = 'One-Off Codec'
            self.ip = ip
    config_consolidation(Codec(input('Enter Codec IP: ')), backup_dict)