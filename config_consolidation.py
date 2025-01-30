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
# BACKUP_FILE = environ.get('CONSOLIDATION_FILE')
# CHECKSUM = environ.get('CONSOLIDATION_FILE_CHECKSUM')
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


def fetch_backup_xml(backup_dict):
    XML = f'''<Command>
        <Provisioning>
            <Service>
                <Fetch>
                    <Checksum item="1" valueSpaceRef="/Valuespace/Vs_string_0_128">{backup_dict['checksum']}</Checksum>
                    <URL item="1" valueSpaceRef="/Valuespace/Vs_string_0_2048">{BACKUP_SERVER_PATH+backup_dict['filename']}</URL>
                </Fetch>
            </Service>
        </Provisioning>
    </Command>'''
    return XML

set_transpile_XML = f'''<Configuration>
        <Macros>
            <EvaluateTranspiled>False</EvaluateTranspiled>
        </Macros>
    </Configuration>'''

# set_bg_xml = '''<Body>
# <Command>
#     <UserInterface>
#         <Branding>
#             <Fetch>
#                 <Checksum>523a916b90ba8286ade4eeafe0c5461155111f8cba3a1401a4ece5ec0b79db61e74f1f996cf134c399fa1abf7bd00df21c11f9a80f2a6080a4ec572d968e1413</Checksum>
#                 <Type>Background</Type>
#                 <URL>http://mmis0177:9000/Wallpapers/NewSplashPageQR4k.png</URL>
#             </Fetch>
#         </Branding>
#     </UserInterface>
# </Command>
# </Body>'''

# def retrieve_extensions(ip):
#     try:
#         response = requests.post(f'http://{ip}/putxml', headers=headers, verify=False, data=retrieve_xml, timeout=10)
#     except requests.exceptions.HTTPError as err:
#         print(err)
#     xml_root = ET.fromstring(response.text)
#     panel_ids = [panel[4].text for panel in xml_root.iter('Panel')]
#     return panel_ids

def http_request(ip, string):
    try:
        response = requests.post(f'http://{ip}/putxml', headers=headers, verify=False, data=string, timeout=180)
        message(response.text, ip)
        return response.text
    except requests.exceptions.HTTPError as err:
        message(f'{ip} -> {err}', ip)

def get_sys_name(ip=''):
    try:
        xml = requests.get(f'http://{ip}/getxml?location=/Configuration/SystemUnit/Name', headers=headers, verify=False, timeout=(10, 30))
        message(xml.text, ip)
        xml_root = ET.fromstring(xml.text)
        sys_name = xml_root[0][0].text
        return sys_name
    except requests.exceptions.HTTPError as err:
        message(err, ip)

def config_consolidation(ip, backup_dict):
    #Getting device information
    sys_name = get_sys_name(ip)

    #Removing macros
    for macro in macros_to_remove:
        http_request(ip, get_rm_macro_string(macro))
        message(macro, sys_name)
    
    #removing UI elements
    for ui in UIs_to_remove:
        http_request(ip, get_rm_UI_string(ui))
        message(ui, sys_name)
    
    #setting EvaluateTranspiled to False
    set_transpile_status = http_request(ip, set_transpile_XML)
    message(f'{set_transpile_status}', sys_name)

    #Fetching and loading backup
    backup_fetch_status = http_request(ip, fetch_backup_xml(backup_dict))
    message(f'{backup_fetch_status}', sys_name)
    
    if backup_fetch_status.find('<ServiceFetchResult status="OK">') != -1:
        message('Update Successful', sys_name)
        return f'{sys_name} - Changes made successfully'
    else:
        message(f'Could not complete consolidation for {sys_name}. Please investigate', sys_name)
        raise custom_exception(f'Could not complete consolidation for {sys_name}. Please investigate.')


if __name__ == '__main__':
    backup = select_backup()
    config_consolidation(input('Enter Codec Ip: '))