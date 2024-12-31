from os import environ
from dotenv import load_dotenv
import requests

#Loading environment varaibles
load_dotenv()

PASSCODE = environ.get('PASSCODE')
headers = {
    'Authorization': f'basic {PASSCODE}',
    'Content-Type': 'text/xml'
}

#Removing insecure http warnings
requests.packages.urllib3.disable_warnings()

#Pre-defining request in order to reduce clutter in other files. Returns text XML unless there's an error.
def cod_post(ip, payload):

    try:
        response = requests.post(f'http://{ip}/putxml', headers=headers, data=payload, verify=False, timeout=(10, 30))
        return response.text
    except requests.exceptions.HTTPError as err:
        print(err.response)
        raise err

if __name__ == '__main__':
    with open('../xml_files/test_post.xml', encoding="utf-8") as f:
        test_xml = f.read()
    result = cod_post('172.16.131.192', test_xml)
    print(result)