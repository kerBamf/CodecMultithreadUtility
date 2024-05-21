import os
import time
import math
from datetime import datetime
# param = '-n' if os.sys.platform().lower()=='win32' else '-c'
hostname = "172.16.131.163" #example
response = os.system(f"ping -c 1 {hostname}")

#and then check the response...
if response == 0:
  print(f"{hostname} is up!")
else:
  print(f"{hostname} is down!")

now = math.floor(time.time())
print(now)

time.sleep(5)

new_now = math.floor(time.time())

print(new_now - now)