from functools import partial


COLOR = 'magenta'

from colorama import init, Fore, Back, Style
init(convert=True, autoreset=True)

# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL


def red_log(b, *a):
    v = ' '.join(map(str, a))
    print(f"{Fore.RED}{b} >> {v}")


def yellow_log(b, *a):
    v = ' '.join(map(str, a))
    print(f"{Fore.YELLOW}{b} >> {v}")


def cyan_log(b, *a):
    v = ' '.join(map(str, a))
    print(f"{Back.GREEN}{b}{Back.RESET}{Fore.WHITE} >> {v}")


def p_cyan_log(word):
    return partial(cyan_log, word)


def p_red_log(word):
    return partial(red_log, word)


def p_yellow_log(word):
    return partial(yellow_log, word)
