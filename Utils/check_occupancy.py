from dotenv import load_dotenv
from os import environ
from cod_get import cod_get
import xml.etree.ElementTree as ET

#Loading environment variables
load_dotenv()
LOGPATH = environ.get('LOGPATH')

request_string = 'status/RoomAnalytics/RoomInUse'

def check_occupancy(ip):
    #checking room count
    count_XML = cod_get(ip, "Status/RoomAnalytics/PeopleCount/Current")
    count_tree = ET.fromstring(count_XML)
    count = count_tree.find(".//Current").text

    #checking presence detection
    presence_XML = cod_get(ip, "Status/RoomAnalytics/PeoplePresence")
    pres_tree = ET.fromstring(presence_XML)
    presence = pres_tree.find('.//PeoplePresence').text
    
    pres_dict = {
        'Occupied': presence,
        'Count': count
    }

    return pres_dict

if __name__ == "__main__":
    print(check_occupancy('172.16.131.163'))
    