from os import environ
from dotenv import load_dotenv
import requests


#Loading environment varaibles
load_dotenv()

PASSCODE = environ.get('PASSCODE')
headers = {
    'Authorization': f'basic {PASSCODE}'
}

#Removing insecure http warnings
requests.packages.urllib3.disable_warnings()

#Pre-defining request in order to reduce clutter in other files. Returns text XML unless there's an error.
def cod_get(ip, path):
    try:
        response = requests.get(f'http://{ip}/getxml?location=/{path}', headers=headers, verify=False, timeout=(10, 30))
        return response.text
    except requests.exceptions.HTTPError as err:
        print(err.response)
        raise err

if __name__ == '__main__':
    info = cod_get('172.16.131.163', 'status/RoomAnalytics/PeopleCount/Current')
    print(info)