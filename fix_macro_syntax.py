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
from Utils.cod_post import cod_post, cod_session_start, cod_session_end
from codec_multithreader import iterator

load_dotenv()


def gen_xml_javascript(string):
    string = string.replace("&", "&amp;")
    string = string.replace("<", "&lt;")
    string = string.replace(">", "&gt;")
    return string


def check_macro(ip, name, javascript, cookie):
    if javascript.find("const xapi = require('xapi');") != -1:
        # print(f"Macro {name} using old syntax. Updating...")
        # if name.find(" ") != -1:
        #     name = name.replace(" ", "&#32;")
        javascript = javascript.replace(
            "const xapi = require('xapi');", "import xapi from 'xapi';"
        )
        javascript = gen_xml_javascript(javascript)

        payload = f"""<Command>
            <Macros>
                <Macro>
                    <Save>
                        <Name>{name}</Name><Transpile>False</Transpile><body>{javascript}</body>
                    </Save>
                </Macro>
            </Macros>
        </Command>"""

        try:
            response = cod_post(ip, payload, cookie)
            return True

        except requests.RequestException as err:
            print(err)
    else:
        return False


def fix_macro_syntax(codec):
    cookie = cod_session_start(codec.ip)

    payload = """<Command>
                    <Macros>
                        <Macro>
                            <Get>
                                <Content>True</Content>
                            </Get>
                        </Macro>
                    </Macros>
                </Command>"""
    try:
        macros_fixed = []
        xml = cod_post(codec.ip, payload, cookie)
        xml_root = ET.fromstring(xml)
        macros = xml_root.findall(".//Macro")
        for element in macros:
            name = element.find(".//Name").text
            javascript = element.find(".//Content").text
            # print(f"{name}\n\r{javascript}")
            macro_fixed = check_macro(codec.ip, name, javascript, cookie)
            if macro_fixed:
                macros_fixed.append(f"{name};")
        if len(macros_fixed) < 1:
            cod_session_end(codec.ip, cookie)
            print("All macros using proper syntax")
            codec.result = "All macros using proper syntax"
            return codec
        else:
            cod_session_end(codec.ip, cookie)
            print(f'Macros Fixed: {" ".join(macros_fixed)}')
            codec.result = f'Macros Fixed: {" ".join(macros_fixed)}'
            return codec

    except requests.RequestException as err:
        print(err)
        cod_session_end(ip, cookie)
        codec.result = err
        return codec

    except ET.ParseError as err:
        print(err)
        cod_session_end(ip, cookie)
        codec.result = err
        return codec


if __name__ == "__main__":

    class Codec:
        def __init__(self, ip):
            self.name = "One-Off Codec"
            self.ip = ip

    ip = input("Enter IP Address: ")
    fix_macro_syntax(Codec(ip))
