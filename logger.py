import datetime
import os
import subprocess

#Checks defined logging directory for a folder with the current date. if one does not exist, it creates a new directory for scripts ran that day
def check_dir(path='', date=''):
    if not os.path.isdir(path + f'/RunLog-{date}'):
        subprocess.run(['mkdir', f'{path}/RunLog-{date}'], capture_output=True)
        return f'/RunLog-{date}'
    else:
        return f'/RunLog-{date}'

#Appends logs to log file (or creates one if one does not exist)
def log_info(string='', sys_name='', log_path=''):
    today = datetime.datetime.now().strftime('%x').replace('/', '-')
    now = datetime.datetime.now().strftime('%X')
    timestamp = f'{today}_{now}'
    filename = f'{sys_name}_log_{today}.txt'
    directory = check_dir(log_path, today)

    with open(f"{log_path}{directory}/{filename}", "a", newline='') as log:
        log.write(f'{timestamp}--> {string}\r\n')
     
    return timestamp


if __name__ == '__main__':
    path = '/Users/pedigoz/Documents/MSK_Coding_Projects/CodecMultithreadUtility/RebootLogs'
    print(log_info('Beef', "Zach", path))