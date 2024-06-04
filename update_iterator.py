import os
import time
from dotenv import load_dotenv
import requests
from urllib3.exceptions import InsecureRequestWarning
from openpyxl import load_workbook
import concurrent.futures
import smtplib
import xml.etree.ElementTree as ET
from chain_update import step_update
from logger import log_info

LOGPATH = os.environ.get('LOGPATH')

xcel = load_workbook(f'./codec_lists/{input("Please input codec file: ")}')
codec_list = xcel.active
codec_list = codec_list.iter_rows(min_row=2, min_col=3, max_col=3, values_only=True)

def message(string):
    print(string)
    log_info(string, 'Master', )

def update_iterator():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(step_update, ip[0]): ip for ip in codec_list}
    
    for future in concurrent.futures.as_completed(futures):
        if (future.exception()):
            message(future.exception())
        else:
            message(future.result())

if __name__ == '__main__':
    update_iterator()
