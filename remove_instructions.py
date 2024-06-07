from os import environ
import requests
import xml.etree.ElementTree as ET
from time import sleep

#Removing insecure http warnings
requests.packages.urllib3.disable_warnings()

#Loading environment variable
PASSCODE = environ.get('PASSCODE')
headers = {
    'Authorization': f'basic {PASSCODE}',
    'Content-Type': 'text/xml'
}

retrieve_xml = '''<Body>
    <Command>
        <UserInterface>
            <Extensions>
                <List>
                    <ActivityType>Custom</ActivityType>
                </List>
            </Extensions>
        </UserInterface>
    </Command>
</Body>'''

remove_macro_xml = '''<Body>
    <Command>
        <Macros>
            <Macro>
                <Remove>
                    <Name>InstructionsPanel</Name>
                </Remove>
            </Macro>
        </Macros>
    </Command>
</Body>'''

remove_instructions_xml = '''<Body>
    <Command>
        <UserInterface>
            <Extensions>
                <Panel>
                    <Remove>
                        <PanelId>instructions</PanelId>
                    </Remove>
                </Panel>
            </Extensions>
        </UserInterface>
    </Command>
</Body>
'''

remove_closeInstructions_xml = '''<Body>
    <Command>
        <UserInterface>
            <Extensions>
                <Panel>
                    <Remove>
                        <PanelId>
                            closeInstructionsHome
                        </PanelId>
                    </Remove>
                </Panel>
            </Extensions>
        </UserInterface>
    </Command>
</Body>
'''

set_ui_xml = '''<Body>
    <Configuration>
        <UserInterface>
            <CustomWallpaperOverlay>Off</CustomWallpaperOverlay>
            <HomeScreen>
                <Dashboard>Off</Dashboard>
            </HomeScreen>
            <OSD>
                <Mode>Auto</Mode>
            </OSD>
        </UserInterface>
        <Standby>
            <Signage>
                <Mode>On</Mode>
                <Url>http://vdvtpwebpban1/mskcontent/channels/30.html</Url>
                <InteractionMode>NonInteractive</InteractionMode>
                <RefreshInterval>720</RefreshInterval>
                <Audio>Off</Audio>
            </Signage>
        </Standby>
    </Configuration>
</Body>'''

set_bg_xml = '''<Body>
<Command>
    <UserInterface>
        <Branding>
            <Fetch>
                <Checksum>523a916b90ba8286ade4eeafe0c5461155111f8cba3a1401a4ece5ec0b79db61e74f1f996cf134c399fa1abf7bd00df21c11f9a80f2a6080a4ec572d968e1413</Checksum>
                <Type>Background</Type>
                <URL>http://mmis0177:9000/Wallpapers/NewSplashPageQR4k.png</URL>
            </Fetch>
        </Branding>
    </UserInterface>
</Command>
</Body>'''

def retrieve_extensions(ip):
    try:
        response = requests.post(f'http://{ip}/putxml', headers=headers, verify=False, data=retrieve_xml, timeout=10)
    except requests.exceptions.HTTPError as err:
        print(err)
    xml_root = ET.fromstring(response.text)
    panel_ids = [panel[4].text for panel in xml_root.iter('Panel')]
    return panel_ids

def remove_instructions(ip):
    
    try:
        response = requests.post(f'http://{ip}/putxml', headers=headers, verify=False, data=remove_macro_xml, timeout=10)
        print(response)
    except requests.exceptions.HTTPError as err:
        print(err)
    
    try:
        response = requests.post(f'http://{ip}/putxml', headers=headers, verify=False, data=remove_instructions_xml, timeout=10)
        print(response)
    except requests.exceptions.HTTPError as err:
        print(err)
    try:
        response = requests.post(f'http://{ip}/putxml', headers=headers, verify=False, data=remove_closeInstructions_xml, timeout=10)
        print(response)
    except requests.exceptions.HTTPError as err:
        print(err)
    try:
        response = requests.post(f'http://{ip}/putxml', headers=headers, verify=False, data=set_bg_xml, timeout=10)
        print(response)
    except requests.exceptions.HTTPError as err:
        print(err)

    sleep(5)

    try:
        response = requests.post(f'http://{ip}/putxml', headers=headers, verify=False, data=set_ui_xml, timeout=10)
        print(response)
    except requests.exceptions.HTTPError as err:
        print(err)
    return f'{ip} - Changes made successfully'

if __name__ == '__main__':
    remove_instructions('172.16.131.60')