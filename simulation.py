import json
import logging
from collections import deque
from processor.machine import DataPath, ControlUnit, IOUnit, IOController
from processor.isa import read_code


def main(code_file, input_file):
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    with open(code_file, "r") as file:
        instructions = json.load(file)
    code = read_code(instructions)
    with open(input_file, "r") as file:
        input_text : str = file.read()
    input_token = deque(map(ord, input_text))
    input_token.appendleft(len(input_token))
    io_unit = IOUnit(input_token)
    io_controller = IOController()
    data_path = DataPath(code, 256, input_token, io_controller)
    control_unit = ControlUnit(code, data_path)
    out, ticks, instr_count =

            if len(out) > 0:
                print(out, "\n-------------------------------")
            print(f"Количество инструкций: {instr_count}")
            print(f"Количество тактов: {ticks}")

        with open(target, mode="rb") as f:
            code = f.read()

        assert code == golden.out["out_code"]
        assert stdout.getvalue() == golden.out["out_stdout"]
        assert caplog.text == golden.out["out_log"]