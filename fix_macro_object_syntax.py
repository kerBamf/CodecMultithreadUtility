import os
from dotenv import load_dotenv
import requests
from openpyxl import load_workbook
import smtplib
import xml.etree.ElementTree as ET
from email.message import EmailMessage
from Utils.logger import log_info
from Utils.excel_parser import excel_parser
from Utils.cod_post import cod_post, cod_session_start, cod_session_end
from codec_multithreader import iterator
from load_backup import load_backup

load_dotenv()


def fix_macro_object_syntax(codec):

    payload = """<Command>
                    <Macros>
                        <Macro>
                            <Get>
                            </Get>
                        </Macro>
                    </Macros>
                </Command>"""
    try:
        cookie = cod_session_start(codec.ip)
        macros_fixed = []
        xml = cod_post(codec.ip, payload, cookie)
        xml_root = ET.fromstring(xml)
        macros = xml_root.findall(".//Macro")
        includes_share_fix = False
        for element in macros:
            name = element.find(".//Name").text
            if name == "Lightware Share Fix":
                shfx_file_obj = {
                    "filename": "ShareFix+DiallerMacros.zip",
                    "checksum": "482bdca7a63b622a7cc67534ec5452253a832a3f09977b83fcbf1451901e923de400fbe0921256102c354a4ee2f86ec4101cfc50797c8afbdac0f3454b226075",
                }
                includes_share_fix = True
                load_backup(codec, shfx_file_obj)
                macros_fixed = ["Lightware Share Fix", "Merged_dialler"]
            elif name == "Merged_dialler" and includes_share_fix == False:
                mrg_file_obj = {
                    "filename": "FixedDialler.zip",
                    "checksum": "949359132912acc4e2e45fe8e52d246e258a9ee89f2fd368c195f5ec9b25f8025a149e8027d73758f3313b890ff95a81645cb249746860c2c3f6f4f2b78eabea",
                }
                load_backup(codec, mrg_file_obj)
                macros_fixed = ["Merged_dialler"]

            # print(f"{name}\n\r{javascript}")
        if len(macros_fixed) < 1:
            cod_session_end(codec.ip, cookie)
            print("All macros using proper syntax")
            codec.response = "All macros using proper syntax"
            return codec
        else:
            cod_session_end(codec.ip, cookie)
            print(f'Macros Fixed: {" ".join(macros_fixed)}')
            codec.response = f'Macros Fixed: {" ".join(macros_fixed)}'
            return codec

    except requests.RequestException as err:
        print(err)
        cod_session_end(ip, cookie)

    except ET.ParseError as err:
        print(err)
        cod_session_end(ip, cookie)


if __name__ == "__main__":

    class Codec:
        def __init__(self, ip):
            self.name = "One-Off Codec"
            self.ip = ip

    ip = input("Enter IP Address: ")
    fix_macro_object_syntax(Codec(ip))
