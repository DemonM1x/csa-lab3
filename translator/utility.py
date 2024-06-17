import re


def is_char(word):
    """Проверка на то, что поданный аргумент символ"""
    match = re.search(r'\'*\'', word)
    if match:
        return 1
    return 0


def is_variable(value):
    return bool(
        re.fullmatch(
            r"^[a-zA-Z_][a-zA-Z_0-9]*:\s*((-?\d+)|(\"[^\"]*\")|(\'[^\']*\')|([bB][fF]\s+\d+))$",
            value,
        )
    )


def is_str(value):
    return bool(re.fullmatch(r"^(\".*\")|(\'.*\')$", value))

def is_int(value):
    return bool(re.fullmatch(r"^-?\d+$", value))
def is_bf(value):
    return bool(re.fullmatch(r"^[bB][fF]\s+\d+$", value))
def is_word(word):
    """Проверка на то, что поданный аргумент слово"""
    match = re.search(r'\w+', word)
    if match:
        return 1
    return 0


def is_num(word):
    """Проверка на то, что поданный аргумент число"""
    try:
        val = int(word)
        return 1
    except ValueError:
        return 0
