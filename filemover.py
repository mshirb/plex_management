import os
import re
import threading
from time import sleep

from LoggerService import WritetoLog

# FOR WINDOWS TESTING
s_dir = 'C:/Users/MarkS/PycharmProjects/plex_management/Test_folder'
s_tv_dir = 'C:/Users/MarkS/PycharmProjects/plex_management/TV'
# FOR LINUX
# s_dir = '/srv/odroid/media/DOWNLOADS'
# s_tv_dir = '/srv/odroid/media/TV'

dir_search_list = []
tv_dir_list = os.listdir(s_tv_dir)
valid = re.compile(r'[sS][0-9]+[eE][0-9]+', re.ASCII)

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
        WritetoLog('FM,BDP','NO MATCH')
    return sresult

class file_moving_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # init_search_list()
        self.KeepRunning = True
        WritetoLog('FM', 'Thread Initialised...')

    def run(self):
        global dir_search_list

        WritetoLog('FM', 'Thread Running...')

        while(self.KeepRunning):

            sleep_timer = 15

            init_search_list()

            if dir_search_list:
                # change sleep timer for more closer checks
                sleep_timer = 2
                for dir in dir_search_list:
                    if not os.path.exists(dir):
                        continue
                    WritetoLog('FM', "Checking {}".format(dir))
                    new_list = os.listdir(dir)
                    for file in new_list:
                        full_path = dir + '/' + str(file)
                        if os.path.isfile(full_path) and (file.endswith('mkv') or file.endswith('avi')):
                            # create name for where the file is to be moved too
                            result = breakdownpath(str(file))
                            # check if it has a folder
                            full_path_folder = s_tv_dir + '/' + result + '/'
                            if not result in tv_dir_list:
                                # Make Directory
                                os.mkdir(full_path_folder)
                            # Move file
                            WritetoLog('FM', 'Moving: ' + full_path)
                            WritetoLog('FM', 'To: ' + full_path_folder + str(file))
                            os.rename(full_path, full_path_folder + str(file))
                        elif os.path.isfile(full_path) and file.endswith('part'):
                            # Not yet finished move on
                            pass
                        elif os.path.isfile(full_path):
                            # Everything else is a file we don't want so delete it
                            os.remove(full_path)
                    if not os.listdir(dir):
                        os.rmdir(dir)

            WritetoLog('FM', "Sleeping for {} minutes".format(sleep_timer))
            sleep(sleep_timer * 60)

if __name__ == "__main__":
    thread = file_moving_thread()
    thread.start()
