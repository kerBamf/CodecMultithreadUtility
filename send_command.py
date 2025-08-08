from os import environ
import requests
import xml.etree.ElementTree as ET
from time import sleep
from Utils.logger import log_info
from Utils.xml_selector import xml_selector
from Utils.cod_post import cod_post
import xml.etree.ElementTree as ET


# Removing insecure http warnings
requests.packages.urllib3.disable_warnings()

# Loading environment variable
PASSCODE = environ.get("PASSCODE")
LOGPATH = environ.get("LOGPATH")
headers = {"Authorization": f"basic {PASSCODE}", "Content-Type": "text/xml"}


# Setting up logger
def message(string, ip, path=LOGPATH):
    log_info(string, ip, path)
    print(string)


def send_command(codec, xml):
    response = cod_post(codec.ip, xml)
    if response.find("Error") != -1:
        codec.result = response
        return codec
    elif response.find('status="OK"') != -1 or response.find("Success") != -1:
        codec.result = f"Command received successfully"
        return codec
    else:
        codec.result = response
        return codec

    # return f'{codec.name} Response: {response.text}'


if __name__ == "__main__":
    new_XML = xml_selector()

    class Codec:
        def __init__(self, ip):
            self.name = "One-Off Codec"
            self.ip = ip

    send_command(Codec(input("Enter codec IP: ")), new_XML)
