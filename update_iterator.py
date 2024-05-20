import os
from dotenv import load_dotenv
import requests
from urllib3.exceptions import InsecureRequestWarning
from openpyxl import load_workbook
import openpyxl
import concurrent.futures
import smtplib
import xml.etree.ElementTree as ET


#Loading excel sheet
#excel_file = f'./codec_lists/{input('Enter codec list filename: ')}'
excel_file = f'./codec_lists/633CodecList.xlsx'
codec_list = load_workbook(excel_file)
ws = codec_list.active

def soft_parse(string):
        string_list = list(string)
        parse_list = []
        period_count = 0
        i = 0
        while period_count < 4:
            if (string_list[i] == '.'):
                period_count += 1
            if (period_count < 4):
                parse_list.append(string_list[i])
            i += 1
        
        parsed_string = ''.join(parse_list)
        return parsed_string

for idx, row in enumerate(ws.iter_rows(min_row=2,values_only=True)):
    ref = idx+2
    row_object = {
        'name': row[1],
        'ip': row[2],
        'soft_ver': soft_parse(row[3]),
        'sys_type': row[4],
    }
    print(row_object)

