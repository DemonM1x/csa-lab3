from __future__ import annotations

import json
import sys

from processor.isa import Opcode, Term


def arithmetic_symbol_to_opcode(symbol):
    return {
        "+": Opcode.ADD,
        "-": Opcode.SUB,
        "*": Opcode.MUL,
        "/": Opcode.DIV,
        "%": Opcode.MOD,
    }.get(symbol)


def meaningful_token(line: str) -> str:
    return line.split(";")[0].strip()


def translate_part1(text):
    labels = {}
    instructions = [{"index": 0, "opcode": Opcode.JMP, "arg": 0, "term": Term(1, 0, "start")}]
    for line_num, line in enumerate(text.splitlines()):
        token = meaningful_token(line)
        if not token:
            continue
        pc = len(instructions)
        if token.endswith(":"):
            label = token[:-1]
            labels[label.lower()] = pc
        elif " " in token:
            instruction_parts = token.split()
            assert len(instruction_parts) == 2, "Invalid instruction: {}".format(token)
            opcode = Opcode(instruction_parts[0])
            instructions.append({"index": pc, "opcode": opcode, "arg": instruction_parts[1], "term": Term(line_num, 0, token)})
        else:
            opcode = Opcode(token)
            instructions.append({"index": pc, "opcode": opcode, "term": Term(line_num, 0, token)})

    return labels, instructions

def translate_part2(labels, instructions):
    for instruction in instructions:
        if "arg" in instruction:
            label = instruction["arg"]
            if not (instruction["opcode"] == Opcode.WORD or instruction == instructions[0]):
                assert label in labels, "Label not defined: " + label
                instruction["arg"] = labels[label]

    instructions[0]["arg"] = labels["start"]

    return instructions



def write_code(instruction_code, target):
    buf = []

    for instr in instruction_code:
        buf.append(json.dumps(instr))
    with open(target, "w") as f:
        f.write("[" + ",\n ".join(buf) + "]")


def main(source, target):
    labels, instructions = translate_part1(source)
    instruction_code = translate_part2(labels, instructions)
    write_code(instruction_code, target)

if __name__ == '__main__':
    assert len(sys.argv) == 3, "Wrong arguments: translator.py <input_file> <target_file>"
    _, source, target = sys.argv
    with open(source, "r", encoding="utf-8") as file:
        code = file.read()
        main(code, target)
