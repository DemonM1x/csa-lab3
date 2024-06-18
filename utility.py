import re

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

