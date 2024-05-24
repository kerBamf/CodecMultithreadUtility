import os
import time
from dotenv import load_dotenv
import requests
from urllib3.exceptions import InsecureRequestWarning
from openpyxl import load_workbook
import openpyxl
import concurrent.futures
import smtplib
import xml.etree.ElementTree as ET
from chain_update import step_update


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

def dummy_func(ip):
    time.sleep(10)
    print("I'm a dummy")
    print(ip)


def update_iterator():
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for ip in codec_list:
                # executor.submit(print, f'{ip} {time.time()}')
                executor.submit(step_update, ip)
    except Exception as error:
        print(error)


if  __name__ == '__main__':
    update_iterator()
    
