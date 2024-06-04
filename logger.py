import datetime
import os
import subprocess

# filepath = os.getcwd()
filepath = os.environ.get('LOGFILEPATH')
print(filepath)

def check_dir(path='', date=''):
    if not os.path.isdir(path + f'/UpdateLog-{date}'):
        subprocess.run('mkdir', f'{path}/UpdateLog-{date}')
        return f'/UpdateLog-{date}'
    else:
        return f'/UpdateLog-{date}'

def log_info(string='', sys_name='', log_path=''):
    today = datetime.datetime.now().strftime('%x')
    now = datetime.datetime.now().strftime('%X')
    timestamp = f'{today}_{now}'
    filename = f'{sys_name}_update_log_{today}.txt'
    filename = filename.replace('/', '-')
    directory = check_dir(filepath, today)

    with open(f"{filepath}{directory}/{filename}", "a", newline='') as log:
        log.write(f'{timestamp}--> {string}\r\n')
     
    return timestamp


if __name__ == '__main__':
    print(log_info('Beef', "Zach"))