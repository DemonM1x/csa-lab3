from __future__ import annotations

import json
import sys
import utility
from processor.isa import Opcode, Term

MIN_INT = -(2**31)
MAX_INT = 2**31 - 1
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
    data_mode = False
    code_mode = False
    instructions = [{"index": 0, "opcode": Opcode.PUSH, "arg": 0, "term": Term(1, 0, "push start")},
                    {"index": 1, "opcode": Opcode.JMP, "term": Term(1, 0, "jmp")}]
    for line_num, line in enumerate(text.splitlines()):
        token = meaningful_token(line)
        if token.lower() == "data:":
            if data_mode or code_mode:
                raise Exception(f"Wrong section on line {line_num}")
            data_mode = True
        if token.lower() == "start:":
            if code_mode:
                raise Exception(f"Wrong section on line {line_num}")
            code_mode = True
            data_mode = False
        if not token:
            continue
        pc = len(instructions)
        if token.endswith(":"):
            label = token[:-1]
            labels[label.lower()] = pc

        elif utility.is_variable(token):
            if data_mode:
                name, value = map(lambda s: s.strip(), token.split(":", maxsplit=1))
                if utility.is_str(value):
                    pstr = [len(value) - 2] + [ord(c) for c in value[1:-1]]
                    labels[name.lower()] = pc
                    instructions.append({"index": pc, "data": name, "arg": pstr[0], "term": Term(line_num, 0, token)})
                    value = value[:-1]
                    for i in range(1, len(value)):
                        pc = len(instructions)
                        instructions.append({"index": pc, "arg": pstr[i], "term": Term(line_num, 0, value[i])})
                elif utility.is_int(value):
                    if MIN_INT <= int(value) <= MAX_INT:
                        labels[name.lower()] = pc
                        instructions.append({"index": pc, "data": name, "arg": int(value), "term": Term(line_num, 0, token)})
                elif utility.is_bf(value):
                    _, size = value.split(maxsplit=1)
                    if int(size) > 0:
                        labels[name.lower()] = pc
                        for d in range(int(size)):
                            instructions.append({"index": pc, "arg": 0, "term": Term(line_num, 0, token)})
                            pc = len(instructions)

                    else:
                        raise Exception(
                            f"Value {value} out of boundaries on line {line_num}"
                        )

        elif " " in token:
            instruction_parts = token.split()
            assert len(instruction_parts) == 2, "Invalid instruction: {}".format(token)
            opcode = Opcode(instruction_parts[0])
            instructions.append(
                {"index": pc, "opcode": opcode, "arg": instruction_parts[1], "term": Term(line_num, 0, token)})
        else:
            opcode = Opcode(token)
            instructions.append({"index": pc, "opcode": opcode, "term": Term(line_num, 0, token)})

    return labels, instructions


def translate_part2(labels, instructions):
    for instruction in instructions:
        if "arg" in instruction and "opcode" in instruction:
            label = str(instruction["arg"])
            if not (label.isdigit()):
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
