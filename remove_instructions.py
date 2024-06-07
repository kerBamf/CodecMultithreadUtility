from os import environ
import requests
import xml.etree.ElementTree as ET

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
            <CustomWallpaperOverlay>
                Off
            </CustomWallpaperOverlay>
            <HomeScreen>
                <Dashboard>
                    Off
                </Dashboard>
            </HomeScreen>
            <OSD>
                <Mode>
                    Auto
                </Mode>
            </OSD>
        </UserInterface>
    </Configuration>
</Body>'''

def retrieve_extensions(ip):
    try:
        response = requests.post(f'http://{ip}/putxml', headers=headers, verify=False, data=retrieve_xml)
    except requests.exceptions.HTTPError as err:
        print(err)
    xml_root = ET.fromstring(response.text)
    panel_ids = [panel[4].text for panel in xml_root.iter('Panel')]
    print(panel_ids)
    return panel_ids

def remove_instructions(ip):
    panels = retrieve_extensions(ip)
    for panel in panels:
        if panel == 'instructions':
            try:
                response = requests.post(f'http://{ip}/putxml', headers=headers, verify=False, data=remove_macro_xml)
                print(response)
            except requests.exceptions.HTTPError as err:
                print(err)
            
            try:
                response = requests.post(f'http://{ip}/putxml', headers=headers, verify=False, data=remove_instructions_xml)
                print(response)
            except requests.exceptions.HTTPError as err:
                print(err)
            try:
                response = requests.post(f'http://{ip}/putxml', headers=headers, verify=False, data=remove_closeInstructions_xml)
                print(response)
            except requests.exceptions.HTTPError as err:
                print(err)
            try:
                response = requests.post(f'http://{ip}/putxml', headers=headers, verify=False, data=set_ui_xml)
                print(response)
            except requests.exceptions.HTTPError as err:
                print(err)
            break
    return 'Changes made successfully'

if __name__ == '__main__':
    remove_instructions('172.16.131.60')