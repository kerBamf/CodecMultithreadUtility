from os import environ
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
from Utils.logger import log_info
from Utils.cod_post import cod_post
from Utils.signage_excel_parser import signage_excel_parser
import concurrent.futures
import openpyxl

# Loading environment variable
load_dotenv()
PASSCODE = environ.get("PASSCODE")
LOGPATH = environ.get("LOGPATH")
headers = {"Authorization": f"basic {PASSCODE}"}


# Setting up logger
def message(string, ip, path=LOGPATH):
    log_info(string, ip, path)
    print(string)


# XML data to be used
def signage_xml(url):
    xml = f"""<Configuration>
    <Standby>
        <Signage>
            <Mode>On</Mode>
            <RefreshInterval>60</RefreshInterval>
            <Url>http://{url}</Url>
        </Signage>
        <Delay>480</Delay>
    </Standby>
    <HttpClient>
        <Mode>On</Mode>
        <AllowHTTP>True</AllowHTTP>
        <AllowInsecureHTTPS>True</AllowInsecureHTTPS>
        <UseHttpProxy>Off</UseHttpProxy>
    </HttpClient>
    <WebEngine>
        <MinimumTLSVersion>TLSv1.2</MinimumTLSVersion>
        <Mode>On</Mode>
        <UseHTTPProxy>Off</UseHTTPProxy>
        <Features>
            <GpuRasterization>On</GpuRasterization>
            <WebGL>On</WebGL>
        </Features>
    </WebEngine>
</Configuration>"""
    return xml


def process(codec):
    payload = signage_xml(codec.url)
    result = cod_post(codec.ip, payload)
    codec.result = result
    message(f"{codec.name} signage configuration result: {result}", codec.name)
    return codec


# Processing signage installation and creating output file
def signage_setup():
    codec_list = signage_excel_parser()
    codecs_processed = [["Name", "IP", "Result"]]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process, codec): codec for codec in codec_list}

    for future in concurrent.futures.as_completed(futures):
        codec = future.result()
        codecs_processed.append([codec.name, codec.ip, codec.result])

    # Creating new Excel file
    new_wb = openpyxl.Workbook()
    new_ws = new_wb.active
    new_ws.title = "SignageInstallationResult"
    ft = openpyxl.styles.Font(bold=True)

    for row in codecs_processed:
        new_ws.append(row)

    for row in new_ws["A1:C1"]:
        for cell in row:
            cell.font = ft

    new_wb.save("../output_files/SignageInstallationResult.xlsx")


if __name__ == "__main__":
    signage_setup()
