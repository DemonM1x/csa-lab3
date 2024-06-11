from __future__ import annotations

import json
from collections import namedtuple

from enum import Enum

class Opcode(str, Enum):
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    MOD = "mod"
    INC = "inc"
    DEC = "dec"

    AND = "and"
    OR = "or"
    XOR = "xor"

    LOAD = "load"
    STORE = "store"
    PUSH = "push"
    DUP = "dup"
    DROP = "drop"
    CLEAR = "clear"

    IN = "in"
    OUT = "out"

    WORD = "word"
    BUF = "buf"
    CALL = "call"
    RET = "ret"

    SWAP = "swap"
    OVER = "over"
    JMP = "jmp"
    JZ = "jz"
    JN = "jn"
    HLT = "hlt"

    def __str__(self):
        return str(self.value)


"""Список всех спец символов"""
correct_words = ["add", "sub", "mul", "div", "mod", "and", "or", "xor", "push", "dup", "drop", "clear", "in", "out", "call", "ret",
                 "swap", "jmp", "jz", "jn", "halt"]

def read_code(filename):

    with open(filename, encoding="utf-8") as file:
        code = json.loads(file.read())

    for instr in code:
        # Конвертация строки в Opcode
        instr["opcode"] = Opcode(instr["opcode"])

        # Конвертация списка term в класс Term
        if "term" in instr:
            assert len(instr["term"]) == 3
            instr["term"] = Term(instr["term"][0], instr["term"][1], instr["term"][2])

    return code

class Term(namedtuple("Term", "line pos symbol")):
    """Описание выражения из исходного текста программы.

    Сделано через класс, чтобы был docstring.
    """



