from os import environ
from dotenv import load_dotenv
import requests

#Loading environment varaibles
load_dotenv()

PASSCODE = environ.get('PASSCODE')
default_headers = {
    'Authorization': f'basic {PASSCODE}',
    'Content-Type': 'text/xml'
}

#Removing insecure http warnings
requests.packages.urllib3.disable_warnings()

#Pre-defining request in order to reduce clutter in other files. Returns text XML unless there's an error.
def cod_post(ip, payload, cookie=None):
    if cookie:
        headers = {'Cookie': f'SessionId={cookie}'}
    else:
        headers = default_headers
    try:
        response = requests.post(f'http://{ip}/putxml', headers=headers, data=payload, verify=False, timeout=(10, 30))
        return response.text
    except requests.exceptions.HTTPError as err:
        print(err.response)
        raise err

#Function for opening a codec session, decreasing latency for multiple-command scripts
def cod_session_start(ip):
    try:
        response = requests.post(f'http://{ip}/xmlapi/session/begin', headers=default_headers, verify=False, timeout=(10, 30))
        print(response.cookies['SessionId'])
        return response.cookies['SessionId']
    except requests.exceptions.HTTPError as err:
        print(err.response)
        raise err
#Needed to end a codec session
def cod_session_end(ip, cookie):
    headers = {'Cookie': f'SessionId={cookie}'}
    try:
        response = requests.post(f'http://{ip}/xmlapi/session/end', headers=headers, verify=False, timeout=(10, 30))
        return response.status_code
    except requests.exceptions.HTTPError as err:
        print(err.response)
        raise err

if __name__ == '__main__':
    with open('../xml_files/test_post.xml', encoding="utf-8") as f:
        test_xml = f.read()
    result = cod_post('172.16.131.192', test_xml)
    print(result)