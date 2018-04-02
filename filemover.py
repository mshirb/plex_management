import os
import re
import threading
from time import sleep
import logging
import argparse

import requests
import pyfttt

ifttt_api_key = ''

# Logger information to print to screen and file
logger = logging.getLogger('thefilemover')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('filemover.log')
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

import platform
if platform.system() == 'Windows':
    print('On Windows')
    s_dir = 'C:/Users/MarkS/PycharmProjects/plex_management/Test_folder'
    s_tv_dir = 'C:/Users/MarkS/PycharmProjects/plex_management/TV'
else:
    print('On Linux')
    s_dir = '/srv/odroid/media/DOWNLOADS'
    s_tv_dir = '/srv/odroid/media/TV'

dir_search_list = []
tv_dir_list = os.listdir(s_tv_dir)
valid = re.compile(r'[sS][0-9]+[eE][0-9]+')
report_sleeping = False

def init_search_list():
    global dir_search_list
    dir_search_list = []
    curr_dir = os.listdir(s_dir)
    for file in curr_dir:
        full_path = s_dir + '/' + str(file)
        if os.path.isdir(full_path):
            dir_search_list.append(full_path)

def breakdownpath(spath):
    global valid
    sresult = spath.upper().replace('.', ' ')
    match = valid.search(sresult)
    if match:
        index = match.start()
        sresult = sresult[:index-1]
    else:
        logger.info('No Match found when breaking down path')
    return sresult

class file_moving_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # init_search_list()
        self.KeepRunning = True
        self.name = 'FileMover'
        logger.debug('Thread Initialised...')

    def run(self):
        global dir_search_list, report_sleeping, ifttt_api_key

        logger.debug('Thread Running...')

        while(self.KeepRunning):

            sleep_timer = 15

            init_search_list()

            if dir_search_list:
                # change sleep timer for more closer checks
                sleep_timer = 2
                for dir in dir_search_list:
                    report_sleeping = False
                    if not os.path.exists(dir):
                        continue
                    logger.info("Checking {}".format(dir))
                    new_list = os.listdir(dir)
                    for file in new_list:
                        full_path = dir + '/' + str(file)
                        if os.path.isfile(full_path) and (file.endswith('mkv') or file.endswith('avi')):
                            # create name for where the file is to be moved too
                            result = breakdownpath(str(file))
                            # check if it has a folder
                            full_path_folder = s_tv_dir + '/' + result + '/'
                            try:
                                # Make Directory
                                os.mkdir(full_path_folder)
                            except FileExistsError:
                                logger.info('Folder already created')
                            # Move file
                            logger.info('Moving: ' + full_path)
                            logger.info('To: ' + full_path_folder + str(file))
                            try:
                                os.rename(full_path, full_path_folder + str(file))
                            except FileExistsError:
                                logger.info('File Already Exists where we are moving it to')
                            else:
                                logger.debug('Informing users')
                                pyfttt.send_event(ifttt_api_key, 'send_plex_email', value1=str(result))
                                try:
                                    logger.debug('Update the library')
                                    requests.get('http://127.0.0.1:32400/library/sections/7/refresh?X-Plex-Token=bK6z5hA66Xb6qST7q8Zx')
                                except Exception:
                                    logger.warning('Doesn\'t appear to have a plex server on this computer')
                        elif os.path.isfile(full_path) and file.endswith('part'):
                            # Not yet finished move on
                            pass
                        elif os.path.isfile(full_path):
                            # Everything else is a file we don't want so delete it
                            os.remove(full_path)
                    if not os.listdir(dir):
                        os.rmdir(dir)

            if not report_sleeping:
                logger.info("Sleeping for {} minutes".format(sleep_timer))
                report_sleeping = True
            sleep(sleep_timer * 60)

if __name__ == "__main__":
    # Parse arguments in for API Keys
    parser = argparse.ArgumentParser()

    # Parse for API Key
    parser.add_argument("ifttt_key", help="IFTTT Webhook API Key", type=str)
    args = parser.parse_args()
    ifttt_api_key = args.ifttt_key

    thread = file_moving_thread()
    thread.start()
