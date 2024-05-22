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



