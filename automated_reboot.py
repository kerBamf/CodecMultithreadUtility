import os
from dotenv import load_dotenv
import time
import math
import subprocess
import requests
from openpyxl import load_workbook
import smtplib
import xml.etree.ElementTree as ET
from email.message import EmailMessage
from Utils.logger import log_info
from Utils.excel_parser import excel_parser
from Utils.cod_post import cod_post
from Utils.cod_get import cod_get
from codec_multithreader import iterator

# Loading Environment Variables
load_dotenv()
PASSCODE = os.environ.get("PASSCODE")
FILENAME = os.environ.get("REBOOT_EXCEL_FILE")
FILEPATH = os.environ.get("REBOOT_EXCEL_PATH")
OUTPUT_PATH = os.environ.get("OUTPUT_FILE_PATH")
LOGPATH = os.environ.get("REBOOT_LOGPATH")

# Disable ssl warning
requests.packages.urllib3.disable_warnings()


# Creating custom exception
class CustomException(Exception):
    pass


# Combining logger and print statement
def message(string="", sys_name=""):
    print(string)
    log_info(string, sys_name, LOGPATH)


# Defining global headers
headers = {"Content-Type": "text/xml", "Authorization": f"basic {PASSCODE}"}


# Function retrieving codec system name for logging purposes
def get_sys_name(codec):
    try:
        xml = cod_get(codec.ip, "Configuration/SystemUnit/Name")
        if xml.find("Error") != -1:
            raise Exception(f"Error connecting to {codec.name}")
        print(xml)
        xml_root = ET.fromstring(xml)
        sys_name = xml_root[0][0].text
        return sys_name
    except requests.HTTPError as err:
        message("HTTP Connection Error", codec.name)
        return "HTTP Connection Error"
    except requests.Timeout as err:
        message("Connection Timeout Error", codec.name)
        return "Connection Timeout Error"
    except requests.RequestException as err:
        message(err, codec.name)
        raise


# Checking active macros on system for necessary reboot macro
def check_macro_status(codec):
    payload = """<Command>
                    <Macros>
                        <Macro>
                            <Get></Get>
                        </Macro>
                    </Macros>
                </Command>"""
    try:
        xml = cod_post(codec.ip, payload)
        xml_root = ET.fromstring(xml)
        macro_active = xml_root.find(".//*[Name='External_Reboot']/Active").text
        print(macro_active)
    except requests.RequestException as err:
        message(f"Could not retrieve macro information from {codec.name}", codec.name)
        raise

    except ET.ParseError as err:
        message(f"Could not find reboot macro on {codec.name}", codec.name)
        raise

    return macro_active


# Base initiate reboot function
def initiate_reboot(codec):

    payload = """<Command>
                    <Standby>
                        <Deactivate></Deactivate>
                    </Standby>
                    <UserInterface>
                        <Message>
                            <Alert>
                                <Display>
                                    <Duration>10</Duration>
                                    <Text>Use touchpanel to cancel reboot</Text>
                                    <Title>AUTOMATED REBOOT INITIATED</Title>
                                </Display>
                            </Alert>
                        </Message>
                    </UserInterface>
                </Command>"""

    try:
        response = cod_post(codec.ip, payload)
        message(response, codec.name)
        return response
    except requests.exceptions.HTTPError as err:
        message(err, codec.name)
        raise


# Reboot Process Function
def automated_reboot(codec):
    try:
        sys_name = get_sys_name(codec)
    except Exception as err:
        codec.result = f"Error reaching {codec.name} - {err}"
        return codec
    message(f"Systname name retrived: {sys_name}", sys_name)
    message("Checking macro status...", sys_name)
    try:
        macro_active = check_macro_status(codec)
    except Exception as err:
        codec.result = f"Error finding macro {codec.name}"
        return codec
    if macro_active == "True":
        message("Initiating reboot...", sys_name)
        initiate_reboot(codec)
    else:
        message(f"Macro deactivated on {codec.name}", codec.name)
        codec.result = f"Macro deactivated on {codec.name}"
        return codec

    time.sleep(10)  # Sleep accounting for alert delay before countdown begins

    message("Reboot initiated. Codec should reboot in 60 seconds", sys_name)

    time.sleep(45)

    def ping():
        return subprocess.run(
            ["ping", "-c", "1", codec.ip], capture_output=True
        ).returncode

    # Pinging codec after sending reboot
    awake = True
    start = math.floor(time.time())
    time_passed = 0
    restarted = False
    message(f"Pinging {sys_name} to confirm shutdown...", sys_name)

    while awake and time_passed < 60:
        ping_var = ping()
        if ping_var:
            awake = False
            restarted = True
            message(f"{sys_name} has shut down. Resuming ping in 1 minute.", sys_name)

        new_time = math.floor(time.time())
        time_passed = new_time - start
        if time_passed % 10 == 0 and time_passed > 0:
            message(f"Still pinging {sys_name}", sys_name)
        time.sleep(1)

    if restarted == False:
        message("Codec did not reboot. Please investigate", sys_name)
        codec.result = f"{sys_name} did not shut down. Please investigate"
        return codec

    time.sleep(60)

    # Resuming ping after restart to confirm codec has rebooted
    time_passed = 0
    start = math.floor(time.time())
    while awake == False and time_passed < 60 * 8:
        ping_var = ping()
        if ping_var == 0:
            awake = True
            message(f"{sys_name} has powered up.", sys_name)

        new_time = math.floor(time.time())
        time_passed = start - new_time
        if time_passed % 10 == 0 and time_passed > 0:
            message(f"Still pinging {sys_name}", sys_name)
        time.sleep(1)

    if awake == False:
        message(f"{sys_name} failed to restart. Please investigate", sys_name)
        codec.result = f"{sys_name} failed to restart. Please investigate"
        return codec

    message(f"{sys_name} reboot successful", sys_name)
    codec.result = f"{sys_name} reboot successful"
    return codec


# Using iterator to multithread over all IPs in a given list

if __name__ == "__main__":
    ip_list = excel_parser(FILEPATH, FILENAME)
    iterator(automated_reboot, ip_list)
