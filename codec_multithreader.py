import os
import datetime
import concurrent.futures
from importlib import import_module
from Utils.excel_parser import excel_parser
from Utils.function_selector import function_selector
from Utils.logger import log_info
from Utils.select_backup import select_backup
from Utils.xml_selector import xml_selector
from Utils.excel_output import excel_output
from Utils.email_utility import email_utility
from dotenv import load_dotenv

# Loading environment variables
load_dotenv()
LOGPATH = os.environ.get("LOGPATH")
OUTPUT_PATH = os.environ.get("OUTPUT_FILE_PATH")


# Logger
def message(string, function):
    print(string)
    log_info(string, function, LOGPATH)


# Multithreading function
def iterator(function, codec_list, file=None):
    # If file exists, executor includes file. Otherwise it proceeds without
    if file:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(function, codec, file): codec for codec in codec_list
            }
    else:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(function, codec): codec for codec in codec_list}

    # Initiating codec list for excel output
    codecs_processed = [["Name", "IP", "Result"]]

    for future in concurrent.futures.as_completed(futures):
        if future.exception():
            #     message(future.exception(), function.__name__)
            # else:
            error = future.exception()
            message(error, function.__name__)
            codec_row = ["Error", "Exception", error]
            codecs_processed.append(codec_row)
        else:
            # print(future.result())
            codec = future.result()
            message(future.result(), function.__name__)
            codec_row = [codec.name, codec.ip, codec.result]
            codecs_processed.append(codec_row)
            # print(codecs_processed)
    date = datetime.datetime.now()
    output_file_name = (
        f"{function.__name__}-{date.strftime('%m')}-{date.strftime('%d')}.xlsx"
    )
    excel_output(
        codecs_processed,
        output_file_name,
    )
    email_utility(
        "codec_multithreader_noreply@mskcc.org",
        "pedigoz@mskcc.org",
        f"{function.__name__}-{date.strftime('%m')}-{date.strftime('%d')} Results",
        "Hello,\r\n\r\nHere are the results from the most recently run multithreader.\r\n\r\nCodec Robit",
        OUTPUT_PATH + output_file_name,
    )
    message("Proccess Completed", function.__name__)


if __name__ == "__main__":
    codec_list = excel_parser()
    selected_function = function_selector()
    if selected_function == "macro_consolidation" or selected_function == "load_backup":
        sup_file = select_backup()
    elif selected_function == "send_command":
        sup_file = xml_selector()
    elif selected_function == "get_info":
        sup_file = input("Enter path: ")
    elif selected_function == "update_nexusCC_contact":
        sup_file = input("Enter New Video ID (no spaces): ")
    else:
        sup_file = None
    imported_func = getattr(import_module(selected_function), selected_function)
    iterator(imported_func, codec_list, sup_file)
