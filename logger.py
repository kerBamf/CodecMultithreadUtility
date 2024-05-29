import datetime
import os

filepath = os.getcwd()
print(filepath)

def log_info(string='', sys_name=''):
    today = datetime.datetime.now().strftime('%x')
    now = datetime.datetime.now().strftime('%X')
    timestamp = f'{today}_{now}'
    filename = f'{sys_name}_update_log_{today}.txt'
    filename = filename.replace('/', '-')

    with open(f"{filepath}/log_files/{filename}", "a", newline='') as log:
        log.write(f'{timestamp}--> {string}\r\n')
     
    return timestamp


if __name__ == '__main__':
    print(log_info('Beef', "Zach"))