import os
from dotenv import load_dotenv
import requests
from urllib3.exceptions import InsecureRequestWarning
from openpyxl import load_workbook
import openpyxl
import concurrent.futures
import smtplib
import xml.etree.ElementTree as ET
from chain_update import chain_update


#Loading excel sheet
#excel_file = f'./codec_lists/{input('Enter codec list filename: ')}'
excel_file = f'./codec_lists/633CodecList.xlsx'
codec_list = load_workbook(excel_file)
ws = codec_list.active

codec_list = [
    '172.16.131.163',
    '172.16.131.13',
    '172.16.131.191'
]

def update_iterator():
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            for ip in codec_list:
                future = executor.submit(chain_update, ip)
                print(future.result())
    except Exception as error:
        print(error)