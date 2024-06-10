import re


def is_char(word):
    """Проверка на то, что поданный аргумент символ"""
    match = re.search(r'\'*\'', word)
    if match:
        return 1
    return 0


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

