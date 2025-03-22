Skip to content
Navigation Menu
AsimALsarhani
-SAP-Job-Automation

Type / to search
Code
Issues
Pull requests
Actions
Projects
Security
Insights
Settings
SAP Job Automation
SAP Job Automation #68
Jobs
Run details
Annotations
1 error
run-automation
failed now in 45s
Search logs
1s
1s
1s
3s
36s
Run python automation.py
  python automation.py
  shell: /usr/bin/bash -e {0}
  env:
    pythonLocation: /opt/hostedtoolcache/Python/3.9.21/x64
    PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.9.21/x64/lib/pkgconfig
    Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.9.21/x64
    Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.9.21/x64
    Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.9.21/x64
    LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.9.21/x64/lib
    SAP_USERNAME: ***
    SAP_PASSWORD: ***
    EMAIL_PASSWORD: ***
INFO:WDM:====== WebDriver manager ======
INFO:WDM:Get LATEST chromedriver version for google-chrome
INFO:WDM:Get LATEST chromedriver version for google-chrome
INFO:WDM:There is no [linux64] chromedriver "134.0.6998.165" for browser google-chrome "134.0.6998" in cache
INFO:WDM:Get LATEST chromedriver version for google-chrome
INFO:WDM:WebDriver version 134.0.6998.165 selected
INFO:WDM:Modern chrome version https://storage.googleapis.com/chrome-for-testing-public/134.0.6998.165/linux64/chromedriver-linux64.zip
INFO:WDM:About to download new driver from https://storage.googleapis.com/chrome-for-testing-public/134.0.6998.165/linux64/chromedriver-linux64.zip
INFO:WDM:Driver downloading response is 200
INFO:WDM:Get LATEST chromedriver version for google-chrome
INFO:WDM:Driver has been saved in cache [/home/runner/.wdm/drivers/chromedriver/linux64/134.0.6998.165]
INFO:__main__:Navigating to SAP login page.
ERROR:__main__:Login failed: Message: 
Stacktrace:
#0 0x55bd08975ffa <unknown>
#1 0x55bd08434970 <unknown>
#2 0x55bd08486385 <unknown>
#3 0x55bd084865b1 <unknown>
#4 0x55bd084d53c4 <unknown>
#5 0x55bd084ac2bd <unknown>
#6 0x55bd084d270c <unknown>
#7 0x55bd084ac063 <unknown>
#8 0x55bd08478328 <unknown>
#9 0x55bd08479491 <unknown>
#10 0x55bd0893d42b <unknown>
#11 0x55bd089412ec <unknown>
#12 0x55bd08924a22 <unknown>
#13 0x55bd08941e64 <unknown>
#14 0x55bd08908bef <unknown>
#15 0x55bd08964558 <unknown>
#16 0x55bd08964736 <unknown>
#17 0x55bd08974e76 <unknown>
#18 0x7f597449caa4 <unknown>
#19 0x7f5974529c3c <unknown>

WARNING:urllib3.connectionpool:Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7fcacfa30490>: Failed to establish a new connection: [Errno 111] Connection refused')': /session/fd1d048c0d4df86fc88798f27e8c6847
0s
1s
0s
