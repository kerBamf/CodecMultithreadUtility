from os import environ
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
from time import sleep
from Utils.logger import log_info
from Utils.xml_selector import xml_selector
from Utils.cod_get import cod_get
import xml.etree.ElementTree as ET


class CustomException(Exception):
    pass


# Loading environment variable
load_dotenv()
PASSCODE = environ.get("PASSCODE")
LOGPATH = environ.get("LOGPATH")
headers = {"Authorization": f"basic {PASSCODE}"}


# Setting up logger
def message(string, ip, path=LOGPATH):
    log_info(string, ip, path)
    print(string)


# Get Codec Name
# def get_sys_name(ip=""):
#     try:
#         xml = cod_get(ip, "Configuration/SystemUnit/Name")
#         xml_root = ET.fromstring(xml)
#         sys_name = xml_root[0][0].text
#         return sys_name
#     except Exception:
#         print(xml)
#         return xml


def get_info(codec, path):
    try:
        # sys_name = get_sys_name(codec.ip)
        response = cod_get(codec.ip, path)
        info_node = path.split("/").pop()
        if response.find(info_node) != -1:
            res_root = ET.fromstring(response)
            res_value = res_root.find(f".//{info_node}")
            res_dict = {"name": codec.name, "response": res_value.text}
            message(f"Response from {codec.name}: {res_value.text}", codec.name)
            return res_dict
        else:
            message(
                f"Unable to retrieve info at {codec.name} --> {response}", codec.name
            )
            raise Exception(f"Unable to retrieve info at {codec.name} --> {response}")

    except Exception as error:
        message(f"Unable to retrieve info at {codec.name} --> {error}", codec.name)
        return f"Unable to retrieve info at {codec.name} --> {error}"


if __name__ == "__main__":

    class Codec:
        def __init__(self, ip):
            self.name = "One-Off Codec"
            self.ip = ip

    info_path = input("Enter path string: ")
    get_info(Codec(input("Enter Codec IP: ")), info_path)
