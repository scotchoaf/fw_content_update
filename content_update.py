'''
Palo Alto Networks classFile.py

testing python classes across files

This software is provided without support, warranty, or guarantee.
Use at your own risk.
'''

import time
import pan.xapi


def get_job_id(s):
    return s.split('<job>')[1].split('</job>')[0]

def get_job_status(s):
    status = s.split('<status>')[1].split('</status>')[0]
    progress = s.split('<progress>')[1].split('</progress>')[0]
    return status, progress

def check_job_status(fw, results):

    # initialize to null status
    status = ''

    job_id = get_job_id(results)
    #print('checking status of job id {0}...'.format(job_id))

    # check job id status and progress
    while status != 'FIN':

        fw.op(cmd='<show><jobs><id>{0}</id></jobs></show>'.format(job_id))
        status, progress = get_job_status(fw.xml_result())
        if status != 'FIN':
            print('job {0} in progress [ {1}% complete ]'.format(job_id, progress), end='\r', flush=True)
            time.sleep(3)

    print('\njob {0} is complete'.format(job_id))

def update_content(fw, type):

    print('checking for latest {0} updates...'.format(type))
    fw.op(cmd='<request><{0}><upgrade><check/></upgrade></{0}></request>'.format(type))

    # download latest content
    print('downloading latest {0} updates...'.format(type))
    fw.op(cmd='<request><{0}><upgrade><download><latest/></download></upgrade></{0}></request>'.format(type))
    results = fw.xml_result()

    if '<job>' in results:
        check_job_status(fw, results)

    # install latest content
    print('installing latest {0} updates...'.format(type))
    fw.op(cmd='<request><{0}><upgrade><install><version>latest</version></install></upgrade></{0}></request>'.format(type))
    results = fw.xml_result()

    if '<job>' in results:
        check_job_status(fw, results)


def main():

    ip_addr = '192.168.55.162'
    user = 'admin'
    pw = 'paloalto'

    fw = pan.xapi.PanXapi(api_username=user, api_password=pw, hostname=ip_addr)

    # get firewall api key
    api_key = fw.keygen()

    # !!! updates require mgmt interface with internet access
    # update to latest content and av versions
    for item in ['content', 'anti-virus']:
        update_content(fw, item)


if __name__ == '__main__':
    main()