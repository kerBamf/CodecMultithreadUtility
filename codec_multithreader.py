import os
import concurrent.futures
from importlib import import_module
from Utils.excel_parser import excel_parser
from Utils.function_selector import function_selector
from Utils.logger import log_info
from dotenv import load_dotenv

#Loading environment variables
load_dotenv()
LOGPATH = os.environ.get('LOGPATH')

#Logger
def message(string, function):
    print(string)
    log_info(string, function, LOGPATH)

#Multithreading function
def iterator(function, ip_list):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(function, ip): ip for ip in ip_list}
    
    for future in concurrent.futures.as_completed(futures):
        if (future.exception()):
            message(future.exception(), function.__name__)
        else:
            message(future.result(), function.__name__)

if __name__ == '__main__':
    ip_list = excel_parser()
    selected_function = function_selector()
    imported_func = getattr(import_module(selected_function), selected_function)
    iterator(imported_func, ip_list)
