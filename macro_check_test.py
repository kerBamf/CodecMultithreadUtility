import os
from dotenv import load_dotenv
import time
import math
import subprocess
import requests
from openpyxl import load_workbook
import smtplib
import xml.etree.ElementTree as ET
from email.message import EmailMessage
from Utils.logger import log_info
from Utils.excel_parser import excel_parser
from Utils.cod_post import cod_post
from codec_multithreader import iterator

load_dotenv()


def check_macro_status(ip):
    payload = """<Command>
                    <Macros>
                        <Macro>
                            <Get>
                                <Name>Lightware Integration</Name>
                                <Content>True</Content>
                            </Get>
                        </Macro>
                    </Macros>
                </Command>"""
    try:
        xml = cod_post(ip, payload)
        xml_root = ET.fromstring(xml)
        macro = xml_root.find(".//*[Name='Lightware Integration']/Content")
        print(macro.text)
        return macro.text

    except requests.RequestException as err:
        print(err)

    except ET.ParseError as err:
        print(err)


def gen_xml_javascript(string):
    string = string.replace("&", "&amp;")
    string = string.replace("<", "&lt;")
    string = string.replace(">", "&gt;")
    return string


def update_macro(ip, javascript):
    if javascript.find("const xapi = require('xapi');") != -1:
        javascript = javascript.replace(
            "const xapi = require('xapi');", "import xapi from 'xapi';"
        )
        javascript = gen_xml_javascript(javascript)
    else:
        print("Codec using proper syntax")
        return

    payload = f"""<Command>
    <Macros>
        <Macro>
            <Save>
                <Name>Lightware Integration</Name><Transpile>False</Transpile><body>{javascript}</body>
            </Save>
        </Macro>
    </Macros>
</Command>"""

    try:

        response = cod_post(ip, payload)
        print(response)
        return response

    except requests.RequestException as err:
        print(err)


if __name__ == "__main__":
    ip = input("Enter IP Address: ")
    macro = check_macro_status(ip)
    update_macro(ip, macro)
