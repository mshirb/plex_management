import datetime

file_header = 'record'

def WritetoLog(thread_id, message):
    dt = datetime.datetime.now()
    file_name = "{}_{}_{}_{}.log".format(file_header, str(dt.year), str(dt.month), str(dt.day))
    with open(file_name, 'a') as f:
        f.write("{}: {}\n".format(thread_id, message))
    print("{}: {}".format(thread_id, message))