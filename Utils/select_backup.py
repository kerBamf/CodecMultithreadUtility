from os import listdir, getcwd, environ
from os.path import isfile, join
from dotenv import load_dotenv
import json

# Loading environment variables
load_dotenv()
server_path = environ.get("BACKUP_SERVER_PATH")
JSON_FILE = environ.get("BACKUP_JSON")


# Loading file dictionary from JSON

raw_json = open("./Utils/backups_json.json", "r", encoding="utf-8")
backups_dict = json.load(raw_json)


# Main function. Generates string to be used in command line while also generating a dictionary to be referenced after user selection is acquired. Returns filename string.
def backup_selector():
    list_dict = {}
    option_string = ""
    for idx, key in enumerate(backups_dict.keys()):
        list_dict.update({idx: key})
        option_string = option_string + f"\t{key}: {idx}\r\n"

    user_options = {"files": list_dict, "string": option_string}

    selection = backups_dict[user_options["files"][user_choice(user_options)]]

    print(selection)
    return selection


# Prints available user choices, then returns selected value to Backup Selector function.
def user_choice(user_options):
    choice = int(
        input(
            f'Select which backup to load to your endpoint(s):\r\n{user_options["string"]}\r\nBackup number selection: '
        )
    )
    for option in list(user_options["files"].keys()):
        if choice == option:
            if "y" == input(
                f'\n\rYou have selected to load {user_options["files"][option]} Proceed? (y/n): '
            ):
                return choice
            else:
                print("Selection Cancelled")
                return user_choice()
    print("Your selection is invalid.")
    return user_choice()


def select_backup():
    selected_backup = backup_selector()
    return selected_backup


if __name__ == "__main__":
    select_backup()
