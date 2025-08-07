from os import environ
from dotenv import load_dotenv
import requests


# Loading environment varaibles
load_dotenv()

PASSCODE = environ.get("PASSCODE")
default_headers = {"Authorization": f"basic {PASSCODE}"}

# Removing insecure http warnings
requests.packages.urllib3.disable_warnings()


# Pre-defining request in order to reduce clutter in other files. Returns text XML unless there's an error.
def cod_get(ip, path, cookie=None):
    if cookie:
        headers = {"Cookie": f"SessionId={cookie}"}
    else:
        headers = default_headers
    try:
        response = requests.get(
            f"http://{ip}/getxml?location=/{path}",
            headers=headers,
            verify=False,
            timeout=(10, 30),
        )
        return response.text
    except requests.HTTPError as err:
        print("HTTP Connection Error")
        return "HTTP Connection Error"
    except requests.Timeout as err:
        print("Connection Timeout Error")
        return "Connection Timeout Error"
    except requests.RequestException as err:
        print(err)
        raise


if __name__ == "__main__":
    info = cod_get("172.16.131.163", "status/RoomAnalytics/PeopleCount/Current")
    print(info)
