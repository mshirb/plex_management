import os
import re
import threading

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
    curr_dir = os.listdir(s_dir)
    for file in curr_dir:
        full_path = s_dir + '/' + str(file)
        if os.path.isdir(full_path):
            dir_search_list.append(full_path)

class file_moving_thread(threading.Thread):
    def __init__(self):
        init_search_list()

    def run(self):
        pass

def breakdownpath(spath):
    global valid
    sresult = spath.upper().replace('.', ' ')
    match = valid.search(sresult)
    if match:
        index = match.start()
        sresult = sresult[:index-1]
    else:
        print('NO MATCH')
    return sresult

if __name__ == "__main__":
    init_search_list()
    for dir in dir_search_list:
        print("Checking {}".format(dir))
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
                print('Moving: ' + full_path)
                print('To: ' + full_path_folder + str(file))
                os.rename(full_path, full_path_folder + str(file))
            elif os.path.isfile(full_path) and file.endswith('part'):
                # Not yet finished move on
                pass
            elif os.path.isfile(full_path):
                # Everything else is a file we don't want so delete it
                os.remove(full_path)
        if not os.listdir(dir):
            os.rmdir(dir)