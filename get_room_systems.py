from os import environ
from os import listdir, getcwd
from os.path import isfile, join
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
from Utils.logger import log_info
from Utils.cod_get import cod_get
from Utils.cod_post import cod_post, cod_session_start, cod_session_end
from Utils.excel_parser import excel_parser
import openpyxl
import concurrent.futures
from dataclasses import dataclass


# **************
# Loading dependencies and file retrieval functionality
# **************


# Loading environment variable
load_dotenv()
PASSCODE = environ.get("PASSCODE")
LOGPATH = environ.get("LOGPATH")
headers = {"Authorization": f"basic {PASSCODE}"}


# Setting up logger
def message(string, ip, path=LOGPATH):
    log_info(string, ip, path)
    print(string)


# Setting Up File Retrieval
def find_path():
    path = f"{getcwd()}/../excel_files"
    return path


def user_choice(files):
    choice = int(
        input(
            f'Select which excel file to use:\r\n{files["options"]}\r\nFile number selection: '
        )
    )
    for key in list(files["files"].keys()):
        if choice == key:
            if "y" == input(
                f'\n\rYou have selected {files["files"][key]} Proceed? (y/n): '
            ):
                return choice
            else:
                print("Selection Cancelled")
                return user_choice()
    print("Your selection is invalid.")
    return user_choice()


def select_file(path):
    file_list = [file for file in listdir(path) if isfile(join(path, file))]
    list_dict = {}
    option_string = ""
    for idx, file in enumerate(file_list):
        list_dict.update({idx: file})
        option_string = option_string + f"\t{file}: {idx}\r\n"

    output = {"files": list_dict, "options": option_string}

    selected_file = output["files"][user_choice(output)]

    return selected_file


# **************************
# Retrieving Info from Codec
# **************************


def startSession(codec):
    try:
        return cod_session_start(codec.ip)
    except Exception as error:
        return error


def check_inputs(codec, cookie):
    try:
        response = cod_get(codec.ip, "Configuration/Video/Input/Connector/Name", cookie)
        root = ET.fromstring(response)
        inputs = root.findall(".//Name")
        for idx, input in enumerate(inputs):
            inputs[idx] = input.text
        return inputs
    except Exception as err:
        return err


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


# Calling functions to fully check system
def check_system(codec):
    if codec.status == "No Response":
        codec.error == "Codec offline. Unable to gather information"
        return codec

    try:
        cookie = startSession(codec)
        vid_inputs = check_inputs(codec, cookie)
        print(vid_inputs)
        # ext_inputs = check_external(codec)
        # lightware = check_lightware(codec)

    except Exception as err:
        codec.error = err
        return err

    # if vid_inputs == True or ext_inputs == True:
    #     codec.ClickShare = "Present"
    # elif vid_inputs == "error" or ext_inputs == "error":
    #     codec.ClickShare = "Unable to retrieve info"
    # else:
    #     codec.ClickShare = "Not Detected"
    # if lightware == True:
    #     codec.Lightware = "Present"
    # elif lightware == "error":
    #     codec.Lightware = "Unable to retrive info"
    # else:
    #     codec.Lightware = "Not Present"

    cod_session_end(codec.ip, cookie)

    # return codec


# ***********************
# Main function
# ***********************


def get_room_systems():
    path = find_path()
    filepath = f"{path}/{select_file(path)}"

    # Loading excel workbook and converting to list of Codec classes
    excel_import = openpyxl.load_workbook(filepath)
    worksheet = excel_import.active

    @dataclass
    class Codec:
        name: str
        ip: str
        type_description: str
        serial: str
        status: str
        error: str
        cameras: str
        input_sources: str
        lightware: str
        lwr_input_sources: str
        output_devices: str

    codec_list = []

    for value in worksheet.iter_rows(
        min_row=2, min_col=2, max_col=12, values_only=True
    ):
        codec = Codec(*value)
        codec_list.append(codec)

    codecs_processed = [
        [
            "System Name",
            "IP Address",
            "Specific System Type Description",
            "Hardware Serial Number",
            "Status",
            "Error",
            "Cameras",
            "Input Sources",
            "Lightware",
            "Lightware Input Sources",
            "Output Devices",
        ]
    ]

    # Feeding through multithreader to obtain data from codecs
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(check_system, codec): codec for codec in codec_list}

    for future in concurrent.futures.as_completed(futures):
        codec = future.result()
        codecs_processed.append(
            [codec.name, codec.ip, codec.ClickShare, codec.Lightware]
        )

    # # Creating new Excel file

    # for row in codecs_processed:
    #     new_ws.append(row)

    # for row in new_ws["A1:C1"]:
    #     for cell in row:
    #         cell.font = ft

    # new_wb.save("../output_files/ClickShareSpreadsheet.xlsx")


if __name__ == "__main__":
    get_room_systems()
