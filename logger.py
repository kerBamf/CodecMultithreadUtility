import datetime
import os
import subprocess

def check_dir(path='', date=''):
    if not os.path.isdir(path + f'/UpdateLog-{date}'):
        subprocess.run(['mkdir', f'{path}/UpdateLog-{date}'], capture_output=True)
        return f'/UpdateLog-{date}'
    else:
        return f'/UpdateLog-{date}'

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
    print(log_info('Beef', "Zach"))