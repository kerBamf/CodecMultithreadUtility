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
BACKUP_FILE = environ.get('CONSOLIDATION_FILE')

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

# Generating checksum based on existing file.
def generate_checksum():
    backup_file = BACKUP_FILE
    raw_checksum = subprocess.run(['shasum', '-a', '512', f'{backup_file}'], capture_output=True, text=True)
    if raw_checksum.stderr == '':
        string = raw_checksum.stdout.split(' ')[0]
    else:
        raise custom_exception(raw_checksum.stderr)
    
    print(string)
    return string

fetch_backup_XML = f'''<Command>
    <Provisioning>
        <Service>
            <Fetch>
                <Checksum item="1" valueSpaceRef="/Valuespace/Vs_string_0_128">e354344d53bbf111916373d91e19d566c77488583d5d14480ffa6bf10c9d0ee4aee91cced187dc134f14e5440ff8daae84106fbe117eb1245c607c904222db42</Checksum>
                <URL item="1" valueSpaceRef="/Valuespace/Vs_string_0_2048">{BACKUP_FILE}</URL>
            </Fetch>
        </Service>
    </Provisioning>
</Command>'''

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
        log_info(response.text, ip, LOGPATH)
        return response.text
    except requests.exceptions.HTTPError as err:
        log_info(f'{ip} -> {err}', ip, LOGPATH)

def get_sys_name(ip=''):
    try:
        xml = requests.get(f'http://{ip}/getxml?location=/Configuration/SystemUnit/Name', headers=headers, verify=False, timeout=(10, 30))
        print(xml.text)
        xml_root = ET.fromstring(xml.text)
        sys_name = xml_root[0][0].text
        return sys_name
    except requests.exceptions.HTTPError as err:
        print(err, ip)

def config_consolidation(ip):
    #Getting device information
    sys_name = get_sys_name(ip)

    #Removing macros
    for macro in macros_to_remove:
        http_request(ip, get_rm_macro_string(macro))
        log_info(macro, sys_name, LOGPATH)
    
    #removing UI elements
    for ui in UIs_to_remove:
        http_request(ip, get_rm_UI_string(ui))
        log_info(ui, sys_name, LOGPATH)
    
    #Fetching and loading backup
    backup_fetch_status = http_request(ip, fetch_backup_XML)
    log_info(f'{backup_fetch_status}', sys_name, LOGPATH)
    
    if backup_fetch_status.find('<ServiceFetchResult status="OK">') != -1:
        log_info('Update Successful', sys_name, LOGPATH)
        return f'{sys_name} - Changes made successfully'
    else:
        log_info(f'Could not complete consolidation for {sys_name}. Please investigate', sys_name, LOGPATH)
        raise custom_exception(f'Could not complete consolidation for {sys_name}. Please investigate.')


if __name__ == '__main__':
    config_consolidation(input('Enter Codec Ip: '))