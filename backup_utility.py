import xml.etree.ElementTree as ET
import datetime
import os
import subprocess
import requests
import json
from dotenv import load_dotenv
from Utils.cod_post import cod_post
from Utils.logger import log_info

# Disable ssl warning
requests.packages.urllib3.disable_warnings()

# Loading environment variables
load_dotenv()
SAVE_PATH = os.environ.get("BACKUP_SAVE_PATH")
PASSCODE = os.environ.get("PASSCODE")
LOGPATH = os.environ.get("LOGPATH")

# Setting up custom exception


class custom_exception(Exception):
    pass


# Setting up logger
def message(string="", sys_name=""):
    print(string)
    log_info(string, sys_name, LOGPATH)


# Setting up headers for HTTP requests:
headers = {"Content-Type": "text/xml", "Authorization": f"basic {PASSCODE}"}


# Function retrieving codec system name for logging purposes
def get_sys_name(codec):
    try:
        xml = requests.get(
            f"http://{codec.ip}/getxml?location=/Configuration/SystemUnit/Name",
            headers=headers,
            verify=False,
            timeout=(10, 30),
        )
        print(xml.text)
        xml_root = ET.fromstring(xml.text)
        sys_name = xml_root[0][0].text
        return sys_name
    except requests.RequestException as err:
        message(f"Backup failed on {codec.name} with this error: {err}", codec.name)
        raise custom_exception(f"Backup failed on {codec.name} with this error: {err}")


# Function retrieving codec configration to be parsed
def get_sys_config(codec):
    try:
        xml = requests.get(
            f"http://{codec.ip}/getxml?location=/Configuration",
            headers=headers,
            verify=False,
            timeout=(10, 30),
        )
        xml_root = ET.fromstring(xml.text)
        return xml_root
    except requests.RequestException as err:
        message(
            f"Failed to pull codec configuration on {codec.name}. Error: {err}",
            codec.name,
        )
        raise custom_exception(f"Backup failed on {codec.name} with this error: {err}")


# Getting Date for use by multiple functions
today = datetime.datetime.now().strftime("%x").replace("/", "-")

# Function retrieving macros

macro_list_xml = f"""<Command>
        <Macros>
            <Macro>
                <Get>
                    <Content>True</Content>
                </Get>
            </Macro>
        </Macros>
    </Command>"""


# Appends strings to new backup file as a line of text
def save_macro(name="", content="", directory="", sys_name=""):
    filename = f"{name}.js"

    try:
        with open(f"{directory}/{filename}", "a", newline="") as file:
            file.write(f"{content}")
        return filename
    except Exception as err:
        message(f"Failed to write macro {name} to file", sys_name)
        raise err


def get_sys_macros(codec, directory="", sys_name=""):
    # First, check for macros
    xml_root = None
    try:
        xml = cod_post(codec.ip, macro_list_xml)
        # print(xml)
        xml_root = ET.fromstring(xml)
        # print(xml_root)
        macro_list = []
        # print(xml_root.findall(".//Macro"))
        for macro in xml_root.findall(".//Macro"):
            macro_name = macro.find("./Name").text
            macro_content = macro.find("./Content").text
            meta = macro.find("./Active").text
            macro_meta = "active" if meta == "True" else "inactive"
            save_macro(macro_name, macro_content, directory, sys_name)
            macro_list.append(
                {
                    "payload": macro_name + ".js",
                    "type": "zip",
                    "id": macro_name,
                    "meta": macro_meta,
                }
            )
            # print(macro_list)

        return macro_list

    except requests.RequestException as err:
        message(
            f"Failed to pull macros from {sys_name}. Error: {err}",
            sys_name,
        )
        raise custom_exception(f"Backup failed on {sys_name} with this error: {err}")

    except ET.ParseError as err:
        message(f"{sys_name} is not using any macros")
        return []


# Checks to see if directory and backup file already exists, and deletes it if it does. This ensures that redundant configurations won't be saved to the same file.
def check_backup_file(sys_name="", save_path=""):
    day_directory = f"{save_path}/Backup_Date_{today}"
    sys_directory = f"{save_path}/Backup_Date_{today}/{sys_name}_{today}"
    if not os.path.isdir(day_directory):
        subprocess.run(["mkdir", f"{day_directory}"], capture_output=True)
    if os.path.isdir(f"{sys_directory}"):
        subprocess.run(["rm", "-rf", sys_directory], capture_output=True)
        subprocess.run(["mkdir", f"{sys_directory}"], capture_output=True)
        message("Old backup deleted. Generating new backup directory", sys_name)
    if not os.path.isdir(sys_directory):
        subprocess.run(["mkdir", f"{sys_directory}"], capture_output=True)


# Appends strings to new backup file as a line of text
def append_file(string="", sys_name="", directory=""):
    filename = "configuration.txt"

    with open(f"{directory}/{filename}", "a", newline="") as file:
        file.write(f"{string}\n")

    return filename


# Recursive XML parsing algorithm converting XML config to .txt file. As each node is visited, the string to be added to the .txt file is built node by node
def parse_xml(root, string="", sys_name="", directory=""):
    try:
        if string == "":
            string = root.tag
        elif root.attrib and len(root.attrib) > 1:
            string = f'{string} {root.tag} {root.attrib["item"]}'
        else:
            string = f"{string} {root.tag}"

        # Checks for child nodes, recursively calling function if they exist, passing the partially built string with it
        if len(root) >= 1:
            for child in root:
                parse_xml(child, string, sys_name, directory)

        # Once the full path of an attribute is reached (the end of a branch in the XML tree), the string is completed and the line appended to the .txt file. Necessary string modifiers for edge cases are in place here to ensure proper syntax in the .txt file.
        else:
            if "Name" in root.tag:
                string = f'{string}: "{root.text}"'
            else:
                string = f"{string}: {root.text}"
            string = (
                string.replace("Configuration", "")
                .replace("None", '""')
                .replace('""""', '""')
            )
            if root.tag == "Parity":
                string = string.replace('""', "None")
            append_file(string, sys_name, directory)

            # Once the line has been appended to the .txt file, the attributes and values of the current node are removed, allowing the string to be reused by the previously called function
            string = string.replace(f": {root.text}", "")
            string = string.replace(f" {root.tag}", "")
            if root.attrib and len(root.attrib) > 1:
                string = string.replace(f' {root.attrib["item"]}', "")
            return
    except Exception as err:
        raise custom_exception("Failed to parse XML")


# Generates manifest, deleting old one if it already exists.
def generate_manifest(sys_name="", directory="", macro_list=[]):
    now = datetime.datetime.now().strftime("%X")
    manifest = {
        "version": "1",
        "profile": {
            "configuration": {
                "items": [
                    {"payload": "configuration.txt", "type": "zip", "id": "_singleton"}
                ]
            },
            "macro": {"items": macro_list},
        },
        "profileName": f"{sys_name}-{now}",
        "generatedAt": f"{now}",
    }
    if os.path.isfile(f"{directory}/manifest.json"):
        subprocess.run(["rm", f"{directory}/manifest.json"])
    with open(f"{directory}/manifest.json", "a", newline="") as file:
        json.dump(manifest, file, indent=2)


# Function compressing generated manifest and configuration file into a .zip folder


def compress_zip(directory="", sys_name=""):
    result = subprocess.run(
        [
            "zip",
            "-r",
            f"./{sys_name}_{today}_backup.zip",
            f"."
        ],
        cwd=f"{directory}",
        capture_output=True,
    )
    print(result.returncode)
    # subprocess.run(
    #     [
    #         "rm",
    #         "-rf",
    #         f"{directory}/{sys_name}_{today}"
    #     ]
    # )
    


# Function generating a sha512 checksum for use by remote backup restoration commands
def generate_checksum(directory="", sys_name=""):
    backup_file = f"{directory}/{sys_name}_{today}_backup.zip"
    filename = "sha512_checksum.txt"
    if os.path.isfile(f"{directory}/{filename}"):
        subprocess.run(["rm", f"{directory}/{filename}"], capture_output=True)
    raw_checksum = subprocess.run(
        ["shasum", "-a", "512", f"{backup_file}"], capture_output=True, text=True
    )
    if raw_checksum.stderr == "":
        string = raw_checksum.stdout.split(" ")[0]
    else:
        raise custom_exception(raw_checksum.stderr)

    print(string)
    with open(f"{directory}/{filename}", "a", newline="") as file:
        file.write(f"{string}")


# Main function
def backup_utility(codec):
    try:
        sys_name = get_sys_name(codec)
        directory = f"{SAVE_PATH}/Backup_Date_{today}/{sys_name}_{today}"
        message(
            f"System name retrieved: {sys_name}\r\nPulling system backup...", sys_name
        )
        config_xml = get_sys_config(codec)
        message("Configuration file retrieved", sys_name)
        message("Checking directory and filename...", sys_name)
        check_backup_file(sys_name, SAVE_PATH)
        message("Parsing XML...", sys_name)
        parse_xml(config_xml, "", sys_name, directory)
        macro_list = get_sys_macros(codec, directory, sys_name)
        message("Generating manifest", sys_name)
        generate_manifest(sys_name, directory, macro_list)
        message("Compressing files...", sys_name)
        compress_zip(directory, sys_name)
        generate_checksum(directory, sys_name)
        message("Backup completed", sys_name)
        resolution = {"Status": "Backup Completed", "System_name": sys_name}
        codec.result = f"Backup on {sys_name} completed"
        return codec
    except Exception as err:
        codec.result = f"Error taking backup: {err}"
        return codec


if __name__ == "__main__":

    class Codec:
        def __init__(self, ip):
            self.name = "One-Off Codec"
            self.ip = ip

    codec_result = backup_utility(Codec(input("Enter codec IP: ")))
    print(codec_result.result)
