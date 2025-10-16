from os import environ
from os import listdir, getcwd
from os.path import isfile, join
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
from Utils.logger import log_info
from Utils.cod_get import cod_get
from Utils.cod_post import cod_post, cod_session_start, cod_session_end
from Utils.excel_parser import excel_parser
import openpyxl
import concurrent.futures
from dataclasses import dataclass


# **************
# Loading dependencies and file retrieval functionality
# **************


# Loading environment variable
load_dotenv()
PASSCODE = environ.get("PASSCODE")
LOGPATH = environ.get("LOGPATH")
headers = {"Authorization": f"basic {PASSCODE}"}


# Setting up logger
def message(string, ip, path=LOGPATH):
    log_info(string, ip, path)
    print(string)


def terminate_all_sessions(codec):
    try:
        get_sesh_xml = f"""<Command>
        <Security>
            <Session>
                <List></List>
            </Session>
        </Security>
    </Command>"""

        response = cod_post(codec.ip, get_sesh_xml)
        root = ET.fromstring(response)
        elements = root.findall(".//Id")
        for element in elements:
            id = element.text
            term_xml = f"""<Command>
    <Security>
        <Session>
            <Terminate>
                <SessionId>{id}</SessionId>
            </Terminate>
        </Session>
    </Security>
</Command>"""

        term_res = cod_post(codec.ip, term_xml)
        return term_res

    except Exception as err:
        return err


if __name__ == "__main__":

    class Codec:
        def __init__(self, ip):
            self.name = "One-Off Codec"
            self.ip = ip

    terminate_all_sessions(Codec(input("Enter Codec IP: ")))
