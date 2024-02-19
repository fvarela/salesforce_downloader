from colorama import init, Fore, Style

class mystyle:
    good = Fore.GREEN + Style.BRIGHT
    bad = Fore.RED + Style.BRIGHT
    bright = Fore.YELLOW + Style.BRIGHT
    green = Fore.GREEN
    done = Style.RESET_ALL
    init(autoreset=True)