# Firewall Content Updates

uses pan-python object to update content and av packs

support direct to NGFW and with Panorama as a proxy

## Direct to NGFW

### requirements

* active NGFW with API access and internet access
* local python needs pip install of pan-python

### to use

run content_update.py with the following switch:

* -f is the firewall ip or hostname
* -u is the admin username
* -p is the admin password

the code will:

* get the fw api key
* check for latest content/threat and antivirus updates
* download and install the latest versions

## Using Panorama as a Proxy

this model makes a Panorama API call and appends the firewall
serial number as a target

### requirements

* active Panorama with API access and internet access
* firewall connected to Panorama
* local python needs pip install of pan-python

### to use

run content_update_w_panorama.py with the following switch:

* -f is the panorama ip or hostname
* -u is the admin username
* -p is the admin password
* -s is the fw serial number

the code will:

* get the panorama api key
* check for latest content/threat and antivirus updates
* download and install the latest versions to the fw referenced