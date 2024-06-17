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

fetch_backup_XML = f'''<Command>
    <Provisioning>
        <Service>
            <Fetch>
                <Checksum item="1" valueSpaceRef="/Valuespace/Vs_string_0_128">053efb937474069987f0f79ae25bc9c5e3a55331ae6fc4c36cbabc1602b7af831c59607f6d9059db9e303e12e2c90aa368f729f0ba448c69d05ed607842c165f</Checksum>
                <URL item="1" valueSpaceRef="/Valuespace/Vs_string_0_2048">http://MMIS0177.mskcc.org:9000/Backup_Files/Macro_Consolidation_Template.zip</URL>
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
    except requests.exceptions.HTTPError as err:
        log_info(f'{ip} -> {err}', ip, LOGPATH)

def config_consolidation(ip):
    #Removing macros
    for macro in macros_to_remove:
        http_request(ip, get_rm_macro_string(macro))
        log_info(macro, ip, LOGPATH)
    
    #removing UI elements
    for ui in UIs_to_remove:
        http_request(ip, get_rm_UI_string(ui))
        log_info(ui, ip, LOGPATH)
    
    #Fetching and loading backup
    http_request(ip, fetch_backup_XML)
    log_info('Backup fetched', ip, LOGPATH)
    
    log_info('Update Successful', ip, LOGPATH)
    return f'{ip} - Changes made successfully'

if __name__ == '__main__':
    config_consolidation(input('Enter Codec Ip: '))