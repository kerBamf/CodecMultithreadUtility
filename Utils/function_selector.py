from os import listdir, getcwd
from os.path import isfile, join

#Loading find relative path
path = getcwd()

def select_function():
    file_list = [file for file in listdir(path) if isfile(join(path, file)) and file.endswith('.py') and file != 'codec_multithreader.py']
    list_dict = {}
    option_string = ''
    for idx, file in enumerate(file_list):
        list_dict.update({idx: file})
        option_string = option_string + f'\t{file}: {idx}\r\n'

    output = {
        'files': list_dict,
        'options': option_string
    }

    selection = output['files'][user_choice(output)]

    return selection

def user_choice(files):
    choice = int(input(f'Select which function to run:\r\n{files["options"]}\r\nFunction number selection: '))
    for key in list(files['files'].keys()):
        if choice == key:
            if 'y' == input(f'\n\rYou have selected to run {files["files"][key]} Proceed? (y/n): '):
                return choice
            else:
                print('Selection Cancelled')
                return user_choice()
    print('Your selection is invalid.')
    return user_choice()

def function_selector():
    selected_function = select_function()
    selected_function = selected_function.replace('.py', '')
    return selected_function

if __name__ == '__main__':
    function_selector()