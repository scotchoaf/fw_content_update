# fw_content_update

uses pan-python to update content and av packs

## requirements

* active NGFW with API access and internet access

## to use

current version has the ip, user, password hardcoded - to update
change these values and run content_update.py

the code will:

* get the api key
* check for latest content/threat and antivirus updates
* download and install the latest versions
