import os
from dotenv import load_dotenv
import concurrent.futures
from importlib import import_module
from urllib3.exceptions import InsecureRequestWarning
from excel_parser import excel_parser
from function_selector import function_selector
from logger import log_info

#Loading environment variables
LOGPATH = os.environ.get('LOGPATH')

ip_list = excel_parser()
selected_function = function_selector()
imported_func = getattr(import_module(selected_function), selected_function)

#function = function_selector()

def message(string):
    print(string)
    log_info(string, 'Master', LOGPATH)

def update_iterator():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(imported_func, ip): ip for ip in ip_list}
    
    for future in concurrent.futures.as_completed(futures):
        if (future.exception()):
            message(future.exception())
        else:
            message(future.result())

if __name__ == '__main__':
    update_iterator()
