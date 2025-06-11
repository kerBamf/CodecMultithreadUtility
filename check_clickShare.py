from os import environ
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
from Utils.logger import log_info
from Utils.cod_get import cod_get
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


def check_hdmi(codec):
    try:
        response = cod_get(codec.ip, "Configuration/Video/Input/Connector/Name")
        response = response.lower().replace(" ", "").replace("-", "")
        if response.find("clickshare") != -1:
            return True
        elif response.find("error") != -1:
            message(f"Unable to retrieve info from {codec.name}", codec.name)
            return "error"
        else:
            return False
    except Exception as error:
        message(f"Unable to retrieve info at {codec.name} --> {error}", codec.name)
        return "error"


external_XML = f"""<Command>
    <UserInterface>
        <Presentation>
            <ExternalSource>
                <List></List>
            </ExternalSource>
        </Presentation>
    </UserInterface>
</Command>"""


def check_external(codec):
    try:
        response = cod_post(codec.ip, external_XML)
        response = response.lower().replace(" ", "").replace("-", "")
        if response.find("clickshare") != -1:
            return True
        elif response.find("error") != -1:
            message(f"Unable to retrieve info from {codec.name}", codec.name)
            return "error"
        else:
            return False
    except Exception as error:
        message(f"Unable to retrieve info at {codec.name} --> {error}", codec.name)
        return "error"


def check_lightware(codec):
    try:
        response = cod_get(codec.ip, "Configuration/Video/Input/Connector/Name")
        response = response.lower().replace(" ", "").replace("-", "")
        if response.find("source") != -1:
            return True
        elif response.find("error") != -1:
            message(f"Unable to retrieve info from {codec.name}", codec.name)
            return "error"
        else:
            return False
    except Exception as error:
        message(f"Unable to retrieve info at {codec.name} --> {error}", codec.name)
        return "error"


def check_inputs(codec):
    vid_inputs = check_hdmi(codec)
    ext_inputs = check_external(codec)
    lightware = check_lightware(codec)

    if vid_inputs == True or ext_inputs == True:
        codec.ClickShare = "Present"
    elif vid_inputs == "error" or ext_inputs == "error":
        codec.ClickShare = "Unable to retrieve info"
    else:
        codec.ClickShare = "Not Detected"
    if lightware == True:
        codec.Lightware = "Present"
    elif lightware == "error":
        codec.Lightware = "Unable to retrive info"
    else:
        codec.Lightware = "Not Present"

    return codec


def check_clickShare():
    # Loading excel workbook
    import_list = excel_parser()
    codecs_processed = [["Name", "IP", "ClickShare", "Lightware"]]

    # Feeding through multithreader to obtain data from codecs
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(check_inputs, codec): codec for codec in import_list}

    for future in concurrent.futures.as_completed(futures):
        codec = future.result()
        codecs_processed.append(
            [codec.name, codec.ip, codec.ClickShare, codec.Lightware]
        )

    # Creating new Excel file
    new_wb = openpyxl.Workbook()
    new_ws = new_wb.active
    new_ws.title = "ClickShare Status"
    ft = openpyxl.styles.Font(bold=True)

    for row in codecs_processed:
        new_ws.append(row)

    for row in new_ws["A1:C1"]:
        for cell in row:
            cell.font = ft

    new_wb.save("../output_files/ClickShareSpreadsheet.xlsx")


if __name__ == "__main__":
    check_clickShare()
