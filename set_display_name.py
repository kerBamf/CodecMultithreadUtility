from dotenv import load_dotenv
from os import environ
from Utils.cod_get import cod_get
from Utils.cod_post import cod_post
from Utils.logger import log_info
import xml.etree.ElementTree as ET

#Loading Environment Variables
load_dotenv()
LOGPATH = environ.get('LOGPATH')

#Setting up logger
def message(string, sys_name):
    print(string)
    log_info(string, sys_name, LOGPATH)

def set_display_name(codec):
    #Retrieving Codec name
    try:
        codec_name = cod_get(codec.ip, "Configuration/SystemUnit/Name")
        name_tree = ET.fromstring(codec_name)
        name = name_tree.find(".//Name").text
    except ET.ParseError as error:
        message(f'Unable to parse name from {codec.name}', codec.name)
        return f'Unable to parse name from {codec.name}'

    #Getting rid of underscore
    display_name = name.replace('_', ' ')
    
    payload = f'''<Configuration>
            <SIP>
                <DisplayName>{display_name}</DisplayName>
            </SIP>
        </Configuration>'''

    response = cod_post(codec.ip, payload)
    message(response, codec.name)
    return response

if __name__ == "__main__":
    class Codec:
        def __init__(self, ip):
            self.name = 'One-Off Codec'
            self.ip = ip

    print(set_display_name(Codec(input('Enter Codec IP: '))))