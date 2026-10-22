import os


def clear_console():
    # 'nt' represents Windows; 'clear' handles macOS and Linux
    os.system('cls' if os.name == 'nt' else 'clear')

def clear_console_ansi():
    # \033[H moves cursor to the top-left; \033[J clears the screen downward
    print("\033[H\033[J", end="")