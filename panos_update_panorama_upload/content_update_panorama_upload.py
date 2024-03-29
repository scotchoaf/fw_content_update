# Copyright (c) 2018, Palo Alto Networks
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# Author: Scott Shoaf <sshoaf@paloaltonetworks.com>

'''
Palo Alto Networks content_update_panorama_upload.py

uses panorama install content updates to a managed firewall
does both content/threat and antivirus updates

This software is provided without support, warranty, or guarantee.
Use at your own risk.
'''

import argparse
import sys
import time
from datetime import datetime, timedelta
import pan.xapi
from xml.etree import ElementTree as etree


def get_job_id(s):
    '''
    extract job-id from pan-python string xml response
    regex parse due to pan-python output join breaking xml rules
    :param s is the input string
    :return: simple string with job id
    '''

    return s.split('<job>')[1].split('</job>')[0]

def get_job_status(s):
    '''
    extract status and progress % from pan-python string xml response
    regex parse due to pan-python output join breaking xml rules
    :param s is the input string
    :return: status text and progress %
    '''

    status = s.split('<status>')[1].split('</status>')[0]
    progress = s.split('<progress>')[1].split('</progress>')[0]
    return status, progress

def check_job_status(fw, results):
    '''
    periodically check job status in the firewall
    :param fw is fw object being queried
    :param results is the xml-string results returned for job status
    '''

    # initialize to null status
    status = ''

    job_id = get_job_id(results)

    # check job id status and progress
    while status != 'FIN':

        fw.op(cmd='<show><jobs><id>{0}</id></jobs></show>'.format(job_id))
        status, progress = get_job_status(fw.xml_result())
        if status != 'FIN':
            print('job {0} in progress [ {1}% complete ]'.format(job_id, progress), end='\r', flush=True)
            time.sleep(5)

    print('\njob {0} is complete'.format(job_id))

def get_latest_content(fw, kind):
    '''
    check panorama to get latest content files
    panorama upload doesn't have a latest option as with the firewall
    :param fw: device object for api calls
    :param type: type of content update to check
    :return:
    '''

    # call to panorama to check content file name
    fw.op(cmd='<request><batch><{0}><info/></{0}></batch></request>'.format(kind))
    results = fw.xml_result()
    contents = etree.fromstring(results)

    # set a year old best date to find the latest one
    bestdate = datetime.now() - timedelta(days=365)

    if kind == 'anti-virus':
        filetype = 'antivirus'
    if kind == 'content':
        filetype = 'contents'

    for item in contents:
        # only consider all-contents file and if downloaded
        if item[7].text == 'yes' and 'all-{0}'.format(filetype) in item[2].text:
            itemdate = datetime.strptime(item[5].text.rsplit(' ', 1)[0],'%Y/%m/%d %H:%M:%S')
            # get the latest date and associated filename
            if itemdate > bestdate:
                bestdate = itemdate
                latestfile = item[2].text

    return latestfile

def update_content(fw, type, sn, filename):
    '''
    check, download, and install latest content updates
    :param fw is the fw object being updated
    :param type is update type - content or anti-virus
    '''

    # install latest content
    # this model assume that panorama has latest content downloads
    print('installing latest {0} updates to {1}'.format(type, sn))
    print('using file {0}'.format(filename))
    fw.op(cmd='<request><batch><{0}><upload-install><devices>{1}</devices>'
              '<file>{2}</file></upload-install>'
              '</{0}></batch></request>'.format(type, sn, filename))
    results = fw.xml_result()

    if '<job>' in results:
        check_job_status(fw, results)


def main():
    '''
    simple set of api calls to update fw to latest content versions
    '''

    # python skillets currently use CLI arguments to get input from the operator / user. Each argparse argument long
    # name must match a variable in the .meta-cnc file directly
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--panorama", help="IP address of Panorama", type=str)
    parser.add_argument("-u", "--username", help="Panorama Username", type=str)
    parser.add_argument("-p", "--password", help="Panorama Password", type=str)
    parser.add_argument("-s", "--serial_number", help="Firewall Serial Number", type=str)
    args = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        parser.exit()
        exit(1)

    # this is actually the panorama ip and will fix
    fw_ip = args.panorama
    username = args.username
    password = args.password
    serial_number = args.serial_number

    # create fw object using pan-python class
    # fw object is actually a panorama object so an api device object
    fw = pan.xapi.PanXapi(api_username=username, api_password=password, hostname=fw_ip)

    # get panorama api key
    api_key = fw.keygen()

    print('updating content for NGFW serial number {0}'.format(serial_number))

    # !!! updates require panorama mgmt interface with internet access
    # update ngfw to latest content and av versions
    # passing in the serial number for device to update

    for item in ['content', 'anti-virus']:
        filename = get_latest_content(fw, item)
        update_content(fw, item, serial_number, filename)

    print('\ncontent update complete')


if __name__ == '__main__':
    main()