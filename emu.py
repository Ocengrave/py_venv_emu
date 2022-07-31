#!/usr/bin/env python3
import os
import subprocess
import sys
import time
from typing import NoReturn

# This is the name of the default virtual environment
venv_name = 'venv'

# This is the name of script to create a bash script
script_name = "script_venv_activate.sh"

# This is default text prefix for install default venv
command_prefix = f"Is this ok? [y/N]:"

ascii_text_terminal = """\t---INIT TERMINAL IN ENV---\n"""


def color_text(text, color):
    """Set colors for text"""
    color_list = {
        'red': f'\033[31m{text}\033[0m',
        'green': f'\033[32m{text}\033[0m',
        'blue': f'\033[34m{text}\033[0m',
        'yellow': f'\033[33m{text}\033[0m',
    }

    if color in color_list:
        return color_list[color]


class User:
    """Base user class"""
    script_path = os.getcwd()

    def __init__(self) -> None:
        self.os_platform = sys.platform
        self.user_env = Venv()
        self.print_user_info()

    def print_user_info(self):
        print(color_text('\n\t--- SYSTEM INFO ---\n', 'yellow'))
        print(color_text('System', 'blue'), f': {self.os_platform}')
        print(color_text('Script Path', 'red'), f': {self.script_path}')

    def validate_user_os(self) -> bool:
        """Validate user OS"""
        valid_script_os = ('linux', 'win32')
        return True if self.os_platform in valid_script_os else False

    @staticmethod
    def run_subprocces(cmd: list) -> None | int:
        if isinstance(cmd, list):
            error_print = color_text("Warning!", "red") \
                          + ": unable to validate the command.\n" \
                            "Try looking at the command in the process call"
            try:
                process = subprocess.run(cmd, stdout=subprocess.PIPE, encoding='utf-8', stderr=subprocess.PIPE)
                print(process)
                return print(error_print) if process.returncode != 0 else True
            except PermissionError:
                return print(error_print)
        print(color_text('Warning!', 'red'), ': wrong command!')

    def run_emu(self, try_start=False) -> bool:
        """
        Setup os env and try runs bash script with venv run command

        :return: result of trying to launch a terminal in ENV

        """
        if self.user_env.find_venv_files(self.script_path):
            print(color_text("\nSuccess!", 'green') + ": your venv folder was found!")
            print(color_text(f'\n{ascii_text_terminal}', 'green'))
            os.environ['PATH'] = self.user_env.setup_venv_path()  # SetUp OS.ENV ['PATH'] in current created venv dir
            script = self.user_env.init_venv_from_bash_script(script_name, self.os_platform)
            if script:
                return True
        else:
            if try_start:
                print(color_text('Warning!', 'red'), ": you are trying to start Python ENV but ENV files not found!")
            return False

    def __create_venv(self, cmd: str, create_bash=False):
        """Read user command, if input call accept then try to install virtual env
           else exit from program"""

        start_time = time.time()  # DEBUG

        command = cmd.lower().strip()
        match command:
            case 'y' | 'yes' | '':
                process_result = self.run_subprocces(['python3', '-m', 'venv', f'{venv_name}', ])
                # process = subprocess.Popen(['python3', '-m', 'venv', f'{venv_name}'],
                #                            stdout=subprocess.PIPE,
                #                            stderr=subprocess.PIPE)
                if process_result:
                    self.user_env.print_output_data()  # optional method
                    print("CREATE TIME: ", time.time() - start_time)  # DEBUG
                    self.run_emu() if create_bash else exit("Terminal emulation wasn't enabled")
            case 'n' | 'no':
                exit("Exit by user command.")
            case _:
                print(color_text('Warning!', 'red'), ": Invalid Command. Try again or exit from script!")
                # Try to call method with new command
                self.__create_venv(input(f"{command_prefix}"), create_bash=True)

    def init_venv(self) -> NoReturn:
        """Init Python virtual env in current script folder"""
        installation_help_text = (
            color_text("Warning!", 'red'),
            ": Your venv folder wasn't found!\n",
            f"- Do you want to install it with the default folder name ",
            f"{color_text('venv', 'green')}?\n ",
            "============================================================",
        )
        if not self.run_emu(try_start=False):
            print(''.join(installation_help_text))
            self.__create_venv(cmd=input(command_prefix), create_bash=True)


class Venv:

    def __init__(self):
        self.path = os.environ["PATH"]

    @staticmethod
    def find_venv_files(user_path):
        """
        Find the venv activation file in the script file directory and return the result
        If the file is not found, return None
        """

        for root, dirs, files in os.walk(user_path):
            for file in files:
                if file == 'activate':
                    path_file = os.path.join(file)
                    return path_file
        else:
            return None

    @staticmethod
    def print_output_data() -> NoReturn:
        """An optional method that generates information about created folders in the environment directory."""
        data_table_format = [
            ["File", "Status"],
            dict()
        ]
        text_for_dict = f" - {color_text('Created!', 'green')}"
        for roots, dirs, files in os.walk(venv_name):
            for direct in dirs:
                data_table_format[1][direct[:15]] = text_for_dict

        # https://ru.stackoverflow.com/questions/1335924/%D0%A1%D0%BE%D0%B7%D0%B4%D0%B0%D0%BD%D0%B8%D0%B5-%D1%82%D0%B0%D0%B1%D0%BB%D0%B8%D1%86%D1%8B-%D0%B2-python
        print('\n{0:^16}|{1:^16}'.format(*data_table_format[0]), '-' * 16 + '+' + '-' * 16,
              '\n'.join('{0:<16}|{1:>16}'.format(*i) for i in data_table_format[1].items()), sep='\n')

    def setup_venv_path(self) -> str:
        self.path = os.path.dirname(venv_name + "/bin/activate") + os.pathsep + os.environ['PATH']
        return self.path

    def init_venv_from_bash_script(self, bash_script_name, os_platform: str) -> int:
        """
        :return: if return code == 0 the user OS doesn't support;
        """
        match os_platform:
            case "linux":
                try:
                    subprocess.call([f'./{bash_script_name}'])
                    return 1
                except FileNotFoundError:
                    with open(f'{bash_script_name}', 'w') as file:
                        file.write(f'#!/bin/bash\n'
                                   f'source {venv_name}/bin/activate\n'
                                   f'rm -f ./{bash_script_name}\n'
                                   f'bash')
                    os.system(f"chmod u+x {bash_script_name}")
                    return self.init_venv_from_bash_script(bash_script_name, os_platform)
            case "win32":
                os.system(f'cmd /k {venv_name}\\scripts\\activate.bat')
                return 1
            case _:
                print(color_text('Warning!', 'red'), ": That script does not support user OS!")
                return 0


def main():
    user = User()
    user.init_venv()


if __name__ == "__main__":
    main()
