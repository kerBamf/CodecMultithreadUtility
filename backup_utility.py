import xml.etree.ElementTree as ET
import datetime
import os
import subprocess
import requests


#Loading environment variables


#Disable ssl warning
requests.packages.urllib3.disable_warnings()

#Loading environment variables
SAVE_PATH = os.environ.get('BACKUP_PATH')

#Checks defined logging directory for a folder with the current date. if one does not exist, it creates a new directory for scripts ran that day
def check_dir(path='', date=''):
    if not os.path.isdir(path + f'/RunLog-{date}'):
        subprocess.run(['mkdir', f'{path}/RunLog-{date}'], capture_output=True)
        return f'/RunLog-{date}'
    else:
        return f'/RunLog-{date}'

#Appends logs to log file (or creates one if one does not exist)
def append_file(string='', sys_name='', log_path=''):
    today = datetime.datetime.now().strftime('%x').replace('/', '-')
    now = datetime.datetime.now().strftime('%X')
    timestamp = f'{today}_{now}'
    filename = f'{sys_name}_log_{today}.txt'
    directory = check_dir(log_path, today)

    with open(f"{log_path}{directory}/{filename}", "a", newline='') as log:
        log.write(f'{string}\n')
     
    return timestamp

#Recursive XML parsing algorithm printing to .txt file.
def parse_xml(root, string=''):
    if string == '':
        string = root.tag
    elif root.attrib and len(root.attrib) > 1:
        string = f'{string} {root.tag} {root.attrib['item']}'
    else:
        string = f'{string} {root.tag}'
    if len(root) >= 1:
        for child in root:
            parse_xml(child, string)
    else:
        if 'Name' in root.tag: 
            string = f'{string}: "{root.text}"'
        else:
            string = f'{string}: {root.text}'
        string = string.replace('Configuration', '').replace('None', '""').replace('""""', '""')
        if root.tag == 'Parity':
            string = string.replace('""', 'None')
        print(string)
        append_file(string, 'XML_Parse_Test', SAVE_PATH)
        string = string.replace(f': {root.text}', '')
        string = string.replace(f' {root.tag}', '')
        if root.attrib and len(root.attrib) > 1:
            string = string.replace(f' {root.attrib['item']}', '')
        return


if __name__ == '__main__':
    parse_xml(xml_root)