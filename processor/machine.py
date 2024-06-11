import logging
import sys
from isa import Opcode, read_code
from processor.signals import Signals


class DataPath:
    def __init__(self, size, input_tokens):
        self.data_stack = []
        self.tos = 0
        self.address_reg = 0
        self.data_memory = [0] * size
        self.data_memory_out = 0
        self.alu_out = 0
        self.arg_tos = 0
        self.arg_address = 0
        self.pc = 0
        self.input_tokens = input_tokens
        self.output_buffer = []
        self.term = None

    def signal_stack_push(self):
        self.data_stack.append(self.tos)

    def signal_stack_pop(self):
        self.data_stack.pop() if self.data_stack != [] else None

    def signal_stack_clear(self):
        self.data_stack.clear()

    def signal_latch_address(self, signal):
        self.address_reg = self.arg_address if signal == Signals.LATCH_ADDR_ARG else self.data_memory_out

    def signal_latch_tos(self, signal):
        buses = {
            Signals.LATCH_TOS_ARG: self.arg_tos,
            Signals.LATCH_TOS_MEM_OUT: self.data_memory_out,
            Signals.LATCH_TOS_FROM_ALU: self.alu_out,
            Signals.LATCH_TOS_FROM_STACK: self.data_stack[-1] if self.data_stack != [] else 0,
            Signals.LATCH_TOS_FROM_PC: self.pc
        }
        self.tos = buses[signal]

    def port_mapping_io(self, code):

        self.pc += 1
        if code == Opcode.IN.value:
            if len(self.input_tokens) == 0:
                raise EOFError()
            input_value = self.input_tokens.pop(0)
            if input_value == '\uFFFF':
                raise ValueError("Null input encountered!")
            self.data_stack.append(ord(input_value))
            logging.info(f"add char '{input_value}' from input buffer")

        elif code == Opcode.OUT.value:
            if self.data_stack:
                output_value = chr(self.tos)
                logging.info(f"add char '{output_value}' to output buffer")
                self.output_buffer.append(output_value)

    def alu(self, operation=Opcode.ADD, left_operand=0):
        self.alu_out = self.tos
        if operation in [Opcode.INC, Opcode.DEC]:
            self.alu_out = self.alu_out + 1 if operation == Opcode.INC else self.alu_out - 1
        elif left_operand != 0:
            oper = self.data_stack[-1] if self.data_stack != [] else 0
            operations = {
                Opcode.ADD: oper + self.tos,
                Opcode.SUB: oper - self.tos,
                Opcode.MUL: oper * self.tos,
                Opcode.DIV: oper / self.tos if self.tos != 0 else 0,
                Opcode.MOD: oper % self.tos if self.tos != 0 else 0,
            }
            self.alu_out = int(operations[operation])

    def zero(self):
        return self.alu == 0


class ControlUnit:
    def __init__(self):
        tick = 0


def simulation(code, input_tokens, data_memory_size, limit):
    """Подготовка модели и запуск симуляции процессора.

    Длительность моделирования ограничена:

    - количеством выполненных инструкций (`limit`);

    - количеством данных ввода (`input_tokens`, если ввод используется), через
      исключение `EOFError`;

    - инструкцией `Halt`, через исключение `StopIteration`.
    """
    data_path = DataPath(data_memory_size, input_tokens)
    control_unit = ControlUnit(code, data_path)
    instr_counter = 0

    logging.debug("%s", control_unit)
    try:
        while instr_counter < limit:
            control_unit.decode_and_execute_instruction()
            instr_counter += 1
            logging.debug("%s", control_unit)
    except EOFError:
        logging.warning("Input buffer is empty!")
    except StopIteration:
        pass

    if instr_counter >= limit:
        logging.warning("Limit exceeded!")
    logging.info("output_buffer: %s", repr("".join(data_path.output_buffer)))
    return "".join(data_path.output_buffer), instr_counter, control_unit.current_tick()


def main(code_file, input_file):
    """Функция запуска модели процессора. Параметры -- имена файлов с машинным
    кодом и с входными данными для симуляции.
    """
    code = read_code(code_file)
    with open(input_file, encoding="utf-8") as file:
        input_text = file.read()
        input_token = []
        for char in input_text:
            input_token.append(char)

    output, instr_counter, ticks = simulation(
        code,
        input_tokens=input_token,
        data_memory_size=100,
        limit=1000,
    )

    print("".join(output))
    print("instr_counter: ", instr_counter, "ticks:", ticks)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    assert len(sys.argv) == 3, "Wrong arguments: machine.py <code_file> <input_file>"
    _, code_file, input_file = sys.argv
    main(code_file, input_file)
