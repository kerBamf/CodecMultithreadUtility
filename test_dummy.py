import os
import time
import math
from datetime import datetime
import xml.etree.ElementTree as ET

from chain_update import check_codec

xml_string = '<?xml version="1.0"?><Command><SystemUnitSoftwareUpgradeResult status="OK"/></Command>'

xml_root = ET.fromstring(xml_string)

if __name__ == '__main__':
  print(xml_root[0].attrib['status'])
  codec_info = check_codec('172.16.131.163')
