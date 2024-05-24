import os
import time
import math
from datetime import datetime
import xml.etree.ElementTree as ET

xml_string = '<?xml version="1.0"?><Command><SystemUnitSoftwareUpgradeResult status="OK"/></Command>'

xml_root = ET.fromstring(xml_string)

if __name__ == '__main__':
  print(xml_root[0].attrib['status'])