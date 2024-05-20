import requests
import xml.etree.ElementTree as ET

software_versions = {
    ''
}

def check_software(ip):
    headers = {'Authorization': 'basic YWRtaW46NzM2NjgzMjk='}
    
    soft_xml = requests.get(f'http://{ip}/getxml?location=/Status/SystemUnit/Software/Version', headers=headers)

    print(soft_xml.text)

    xml_root = ET.fromstring(soft_xml.text)

    parsed_version = xml_root[0][0][0].text.replace('ce','').split('.')

    return parsed_version

def upgrade

# check_software('172.16.131.163')
def chain_update(ip):

    version_nums = check_software('172.16.131.163')

    if (version_nums[0] == 11 and version_nums[1] == 14):
        return

    current = version_nums

    if (version_nums[0] < 10):
        if (version_nums[1] < 15):
            print('upgrade to version 9.15.3.22')
        else:
            print('Upgrade to version 10.15.4')
    elif (version_nums[0] == 10):
        if (version_nums[1] < 15):
            print('Upgrade to version 10.15.4')
        elif (version_nums[1] >= 15 and version_nums[1] < 19):
            print('Upgrade to version 10.19.4.2')
        else:
            print('Upgrade to version 11.1.2.4')
    elif (version_nums[0] == 11):
        if (version_nums[1] < 9):
            print('Upgrade to version 11.9')
        elif (version_nums[1] >= 9 and version_nums < 14):
            print('Upgrade to version 11.14')


