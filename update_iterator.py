import os
import time
from dotenv import load_dotenv
import requests
from urllib3.exceptions import InsecureRequestWarning
from openpyxl import load_workbook
import concurrent.futures
import smtplib
import xml.etree.ElementTree as ET
from excel_parser import excel_parser
from chain_update import chain_update
from logger import log_info

LOGPATH = os.environ.get('LOGPATH')

ip_list = excel_parser()

def message(string):
    print(string)
    log_info(string, 'Master', LOGPATH)

def update_iterator():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(chain_update, ip): ip for ip in ip_list}
    
    for future in concurrent.futures.as_completed(futures):
        if (future.exception()):
            message(future.exception())
        else:
            message(future.result())

if __name__ == '__main__':
    update_iterator()
