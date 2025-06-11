from os import environ
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
from Utils.logger import log_info
from Utils.cod_post import cod_post
from Utils.excel_parser import excel_parser
import openpyxl
import concurrent.futures


class CustomException(Exception):
    pass


# Loading environment variable
load_dotenv()
PASSCODE = environ.get("PASSCODE")
LOGPATH = environ.get("LOGPATH")
headers = {"Authorization": f"basic {PASSCODE}"}


# Setting up logger
def message(string, ip, path=LOGPATH):
    log_info(string, ip, path)
    print(string)


macro_XML = f"""<Command>
    <Macros>
        <Macro>
            <Get>
                <Name>Merged_dialler</Name>
            </Get>
        </Macro>
    </Macros>
</Command>"""


def check_dialer(codec):
    try:
        response = cod_post(codec.ip, macro_XML)
        print(response)
        if response.find('status="OK"') != -1:
            return True
        elif response.find("No such macro") != -1:
            message(f"Macro does not exist on {codec.name}", codec.name)
            return False
        else:
            message(f"Unable to retrieve info from {codec.name}", codec.name)
            return "error"
    except Exception as error:
        message(f"Unable to retrieve info at {codec.name} --> {error}", codec.name)
        return "error"


# Runs API request and modifies codec object for later use by openpyxl
def process(codec):
    macro_status = check_dialer(codec)

    if macro_status == True:
        codec.Dialer = "Present"
    elif macro_status == False:
        codec.Dialer = "Not Detected"
    elif macro_status == "error":
        codec.Dialer = "Unable to retrieve info"

    return codec


def check_dialer_macro():
    # Loading excel workbook
    import_list = excel_parser()
    codecs_processed = [["Name", "IP", "Dialer"]]

    # Feeding through multithreader to obtain data from codecs
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process, codec): codec for codec in import_list}

    for future in concurrent.futures.as_completed(futures):
        codec = future.result()
        codecs_processed.append([codec.name, codec.ip, codec.Dialer])

    # Creating new Excel file
    new_wb = openpyxl.Workbook()
    new_ws = new_wb.active
    new_ws.title = "DialerStatus"
    ft = openpyxl.styles.Font(bold=True)

    for row in codecs_processed:
        new_ws.append(row)

    for row in new_ws["A1:C1"]:
        for cell in row:
            cell.font = ft

    new_wb.save("../output_files/DialerResults.xlsx")


if __name__ == "__main__":
    check_dialer_macro()
