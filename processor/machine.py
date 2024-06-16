import logging
import sys
from collections import deque

from isa import Opcode, read_code
from processor.signals import Signals


class DataPath:
    def __init__(self, code, size, input_tokens):
        self.data_stack = []
        self.tos = 0

        self.address_reg = 0
        self.data_memory = [0] * size
        self.data_memory_out = 0
        self.buffer_register = 0
        self.alu_out = 0
        self.arg_tos = 0
        self.arg_address = 0
        self.pc = 0
        self.input_tokens = input_tokens
        self.input_token = 0
        self.output_buffer = []
        self.term = None
        for index, _ in enumerate(code):
            self.data_memory[index] = code[index]

    def signal_stack_push(self):
        self.data_stack.append(self.tos)

    def signal_stack_pop(self):
        self.data_stack.pop() if self.data_stack != [] else None

    def signal_stack_clear(self):
        self.data_stack.clear()
    def latch_buffer_register(self):
        self.buffer_register = self.data_stack[-1]
    def signal_latch_address(self, signal: Signals):
        self.address_reg = self.tos if signal == Signals.LATCH_ADDR_TOS else self.pc

    def signal_latch_tos(self, signal):
        buses = {
            Signals.LATCH_TOS_ARG: self.arg_tos,
            Signals.LATCH_TOS_MEM_OUT: self.memory_read(),
            Signals.LATCH_TOS_FROM_ALU: self.alu_out,
            Signals.LATCH_TOS_FROM_STACK: self.data_stack[-1] if self.data_stack != [] else 0,
            Signals.LATCH_TOS_FROM_PC: self.pc,
            Signals.LATCH_TOS_INPUT: self.input_token,
            Signals.LATCH_TOS_BR: self.buffer_register
        }
        self.tos = buses[signal]

    def memory_read(self):
        return self.data_memory[self.address_reg]["arg"]

    def memory_write(self):
        self.data_memory[self.address_reg] = self.data_stack[-1]
    def port_mapping_io(self, code):

        if code == Opcode.IN.value:
            if len(self.input_tokens) == 0:
                raise EOFError()
            input_value = self.input_tokens.pop(0)
            if input_value == '\uFFFF':
                raise ValueError("Null input encountered!")
            logging.info(f"add char '{input_value}' from input buffer")
            return input_value

        elif code == Opcode.OUT.value:
            if self.data_stack:
                if 32 <= self.tos <= 127:
                    output_value = chr(self.tos)
                else:
                    output_value = str(self.tos)
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
        return self.tos == 0


class ControlUnit:
    def __init__(self, instructions, data_path: DataPath):
        self.instructions = instructions
        self.instruction = instructions[0]
        self.instr_count = 1
        self.data_path = data_path
        self.pc = 0
        self.return_stack = deque()
        self._tick = 0

    def tick(self):
        """Продвинуть модельное время процессора вперёд на один такт."""
        if self._tick < 1000:
            logging.debug(self)
            if self._tick == 999:
                logging.info("Cut log due to its size")
        self._tick += 1



    def current_tick(self):
        """Текущее модельное время процессора (в тактах)."""
        return self._tick

    def signal_latch_program_counter(self, signal):
        self.instruction = self.instructions[self.pc]
        self.data_path.term = self.instruction["term"]
        self.data_path.arg_tos = self.instruction["arg"] if "arg" in self.instruction else 0
        self.data_path.arg_address = self.instruction["arg"] if "arg" in self.instruction else 0
        if signal == Signals.PC_JZ:
            if self.data_path.zero():
                self.pc = self.data_path.data_stack[-1]
            else:
                self.pc += 1
        if signal == Signals.PC_JN:
            if self.data_path.tos < 0:
                self.pc = self.data_path.data_stack[-1]
            else:
                self.pc += 1
        if signal == Signals.PC_RS:
            if len(self.return_stack) == 0:
                raise Exception("Empty return stack")
            self.pc = self.return_stack[-1]

        if signal == Signals.PC_JUMP:
            self.pc = self.data_path.tos

        if signal == Signals.PC_NEXT:
            self.pc += 1

        self.data_path.pc = self.pc

    def execute_control_flow_instruction(self, opcode):
        if opcode is Opcode.HLT:
            raise StopIteration()
        if opcode is Opcode.JMP:
            self.signal_latch_program_counter(Signals.PC_JUMP)
            self.tick()
            self.data_path.signal_latch_tos(Signals.LATCH_TOS_FROM_STACK)
            self.tick()
            self.data_path.signal_stack_pop()
            self.tick()

        if opcode is Opcode.JZ:
            self.signal_latch_program_counter(Signals.PC_JZ)
            self.tick()
            self.data_path.signal_stack_pop()
            self.tick()
            self.data_path.signal_latch_tos(Signals.LATCH_TOS_FROM_STACK)
            self.tick()
            self.data_path.signal_stack_pop()
            self.tick()

        if opcode is Opcode.JN:
            self.signal_latch_program_counter(Signals.PC_JN)
            self.tick()
            self.data_path.signal_stack_pop()
            self.tick()
            self.data_path.signal_latch_tos(Signals.LATCH_TOS_FROM_STACK)
            self.tick()
            self.data_path.signal_stack_pop()
            self.tick()

        if opcode is Opcode.RET:
            self.signal_latch_program_counter(Signals.PC_RS)
            self.tick()
            self.return_stack.pop()
            self.tick()
        if opcode is Opcode.CALL:
            self.return_stack.append(self.pc + 1)
            self.tick()
            self.signal_latch_program_counter(Signals.PC_JUMP)
            self.tick()
            self.data_path.signal_latch_tos(Signals.LATCH_TOS_FROM_STACK)
            self.tick()
            self.data_path.signal_stack_pop()
            self.tick()

    def decode_and_execute_instruction(self):
        instr = self.instructions[self.pc]
        opcode = instr["opcode"]
        if self.execute_control_flow_instruction(opcode):
            return

        elif opcode in {Opcode.INC, Opcode.DEC, Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV, Opcode.MOD}:
            self.data_path.alu(opcode)
            self.tick()
            self.data_path.signal_latch_tos(Signals.LATCH_TOS_FROM_ALU)
            self.signal_latch_program_counter(Signals.PC_NEXT)
            self.tick()

        elif opcode is Opcode.CLEAR:
            self.data_path.signal_stack_clear()
            self.tick()

        elif opcode is Opcode.LOAD:
            self.data_path.signal_latch_address(Signals.LATCH_ADDR_TOS)
            self.tick()
            self.data_path.signal_latch_tos(Signals.LATCH_TOS_MEM_OUT)
            self.signal_latch_program_counter(Signals.PC_NEXT)
            self.tick()

        elif opcode is Opcode.STORE:
            self.data_path.signal_latch_address(Signals.LATCH_ADDR_TOS)
            self.tick()
            self.data_path.memory_write()
            self.tick()

        elif opcode is Opcode.DUP:
            self.data_path.signal_stack_push()
            self.tick()
            self.signal_latch_program_counter(Signals.PC_NEXT)
            self.tick()

        elif opcode is Opcode.NOP:
            self.signal_latch_program_counter(Signals.PC_NEXT)
            self.tick()

        elif opcode is Opcode.PUSH:
            self.data_path.signal_stack_push()
            self.tick()
            self.data_path.signal_latch_address(Signals.LATCH_ADDR_FROM_MEM)
            self.tick()
            self.data_path.signal_latch_tos(Signals.LATCH_TOS_MEM_OUT)
            self.signal_latch_program_counter(Signals.PC_NEXT)
            self.tick()

        elif opcode is Opcode.DROP:
            self.data_path.signal_latch_tos(Signals.LATCH_TOS_FROM_STACK)
            self.tick()
            self.data_path.signal_stack_pop()
            self.signal_latch_program_counter(Signals.PC_NEXT)
            self.tick()
        elif opcode is Opcode.SWAP:
            self.data_path.latch_buffer_register()
            self.tick()
            self.data_path.signal_stack_pop()
            self.tick()
            self.data_path.signal_stack_push()
            self.tick()
            self.data_path.signal_latch_tos(Signals.LATCH_TOS_BR)
            self.signal_latch_program_counter(Signals.PC_NEXT)
            self.tick()

        elif opcode is Opcode.OVER:
            self.data_path.latch_buffer_register()
            self.tick()
            self.data_path.signal_stack_pop()
            self.tick()
            self.data_path.signal_stack_push()
            self.tick()
            self.data_path.signal_latch_tos(Signals.LATCH_TOS_BR)
            self.tick()
            self.data_path.latch_buffer_register()
            self.tick()
            self.data_path.signal_stack_push()
            self.tick()
            self.data_path.signal_latch_tos(Signals.LATCH_TOS_BR)
            self.signal_latch_program_counter(Signals.PC_NEXT)
            self.tick()

        elif opcode is Opcode.IN:
            self.data_path.signal_latch_tos(Signals.LATCH_TOS_INPUT)
            self.signal_latch_program_counter(Signals.PC_NEXT)
            self.tick()

        elif opcode is Opcode.OUT:
            self.data_path.port_mapping_io(opcode)
            self.tick()
            self.data_path.signal_latch_tos(Signals.LATCH_TOS_FROM_STACK)
            self.tick()
            self.data_path.signal_stack_pop()
            self.signal_latch_program_counter(Signals.PC_NEXT)
            self.tick()

    def __repr__(self):
        """Вернуть строковое представление состояния процессора."""
        state_repr = "TICK: {:3} PC: {:3} ADDR: {:3} MEM_OUT: {} DS: {}".format(
            self._tick,
            self.pc,
            self.data_path.address_reg,
            self.data_path.data_memory[self.data_path.address_reg]["arg"],
            self.data_path.data_stack,
        )
        instr = self.instructions[self.pc]
        opcode = instr["opcode"]
        instr_repr = str(opcode)
        if "arg" in instr:
            instr_repr += " {}".format(instr["arg"])

        if "term" in instr:
            term = instr["term"]
            instr_repr += "  ('{}'@{}:{})".format(term.symbol, term.line, term.pos)

        return "{} \t{}".format(state_repr, instr_repr)

def simulation(code, input_tokens, data_memory_size, limit):
    """Подготовка модели и запуск симуляции процессора.

    Длительность моделирования ограничена:

    - количеством выполненных инструкций (`limit`);

    - количеством данных ввода (`input_tokens`, если ввод используется), через
      исключение `EOFError`;

    - инструкцией `Halt`, через исключение `StopIteration`.
    """
    data_path = DataPath(code, data_memory_size, input_tokens)
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
