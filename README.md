# Архитектура компьютера. Лабораторная работа №3
- Подольский Вячеслав Ильич, P3220
- asm | stack | neum | hw | instr | struct | stream | port | pstr | prob1 
- Упрощенный вариант


## Содержание

1. [Язык программирования](#язык-программирования)
2. [Организация памяти](#организация-памяти)
3. [Система команд](#система-команд)
4. [Транслятор](#транслятор)
5. [Модель процессора](#модель-процессора)
6. [Тестирование](#тестирование)
7. [Пример использования](#пример-использования)
8. [Пример тестирования исходного кода](#пример-тестирования-исходного-кода)
9. [Статистика](#статистика)


## Язык программирования

### Синтаксис

```ebnf
<program> ::= <section_data>? <section_code>

<section_data> ::= "section data:" <comment>? "\n" <data_line>*
<data_line> ::= <variable> <comment>? "\n"

<variable> ::= <variable_name> ":" <variable_value>
<variable_name> ::= <letter_with_underscore> <letter_or_number_with_underscore>*
<variable_value> ::= <integer>
                   | <string>
                   | <buffer>

<section_code> ::= "section code:" <comment>? "\n" <code_line>*
<code_line> ::= (<label> | <command>) [comment] "\n"

<label> ::= <label_name> ":"
<label_name> ::= <letter_with_underscore> <letter_or_number_with_underscore>*

<command> ::= op0 | op1

<op0> ::= "nop"
        | "drop"
        | "swap"
        | "dup"
        | "over"
        | "inc"
        | "dec"
        | "add"
        | "sub"
        | "mul"
        | "div"
        | "mod"
        | "load"
        | "store"
        | "in"
        | "out"
        | "jmp"
        | "jz"
        | "call"
        | "ret"
        | "hlt"

<op1> ::= "push" <integer>
        | "push" <variable_name>
        | "push" <label_name>

<lowercase_letter> ::= [a-z]
<uppercase_letter> ::= [A-Z]
<letter> ::= <lowercase_letter> | <uppercase_letter>

<integer> ::= [ "-" ] { <any of "0-9"> }

<single_quote> ::= "\'"
<double_quote> ::= "\""
<string> ::= <single_quote> [^\"\n]* <single_quote>
           | <double_quote> [^\'\n]* <double_quote>

<buffer> ::= "bf" positive_integer

<comment> ::= ";" [^\n]*
```

### Семантика

- Код выполняется последовательно, одна инструкция за другой.
Список доступных инструкций см. [система команд](#система-команд)

- В коде данные объявляются в специальном разделе `data`, в котором могут быть 
  объявлены переменные (числа, строки, буферы). Секция данных обязана 
  находиться до секции кода. Типизация переменных статическая.
- Метки определяются на отдельной строке исходного кода:

```asm
label:
        push 1
```
Метки могут быть использованы
до или после определения в исходном коде:
```asm
test:
      push label
      jmp
```
- Метки в коде программы представляют собой
  именованные точки,  на которые можно ссылаться
  из других частей программы. Они не различаются
 по регистру (например, label и LaBeL считаются одной и той же меткой).
 Каждая метка должна быть уникальной,
 и повторное их определение недопустимо.

Метки могут быть использованы множество раз в коде, компилятор
заменит каждое упоминание метки адресом инструкции, следующей за её определением.

- Любая программа обязана иметь метку `start`, указывающую
на первую исполняемую команду.


### Организация памяти:

- Вся внешняя память - статическая
- Память соответствует фон Неймановской архитектуре.
- Машинное слово – не определено. Реализуется высокоуровневой
  структурой данных. 
* Адресация – прямая абсолютная.

```text
            Memory
+------------------------------+
| 00  : push start address (n) |
| 01  : jmp                    |
|    ...                       |
| s+0 : string length          |
| s+1 : string value           |
|    ...                       |
| b+0 : buffer (0)             |
| b+1 : buffer (0)             |
|    ...                       |
| n   : program start          |
| n+1 : instruction            |
|    ...                       |
| 7 : PUSH sub                 |
| 8 : CALL                     |
|    ...                       |
| 25  : subprogram instruction |
| 26  : RET                    |
|    ...                       |
|  n  : HLT                    |
+------------------------------+

```
- Ячейка памяти `0` - отправка адресса первой интрукции программы.
  Ячейка памяти `01` - безусловный переход на первую интрукцию.

Организация стека:

* Стек реализован в виде отдельного регистра, представляющего вершину
  стека (`TOS`) + высокоуровневой структуры данных deque.
* Стек 32-разрядный и позволяет полностью помещать один операнд одной ячейки памяти.

## Система команд

Особенности процессора:

- Машинное слово – не определено.
- Доступ к памяти осуществляется по адресу из специального регистра.
  Значение в нем может быть защелкнуто либо из PC, либо из вершины стека
- Обработка данных осуществляется в стеке. Данные попадают в стек из
  памяти, либо из устройств ввода/вывода.
- Поток управления:
    Значение `PC` инкрементируется после исполнения каждой инструкции,
    Условные (`JZ`) и безусловные (`JMP`) переходы.

Набор инструкций:

 Операции над стеком:
  - `push [number]`  - поместить число в top of the stack.
  - `drop`  - удалить значение с вершины стека данных.
  - `load`  - загрузить из памяти значение по адресу с вершины стека.
  - `store`  - положить значение в память по указанному адресу.
  - `clear` - очистить стек данных.

Операции потока программы:
  - `NOP` – нет операции.
  - `jmp`  - совершить безусловный переход по адрессу из top of the stack
  - `jz`  - если элемент равен 0,
  начать исполнять инструкции по указанному адресу.
  - `call`  - начать исполнение процедуры по указанному адресу.
  - `ret`  - вернуться из процедуры в основную программу, на следующий адрес.

  - `hlt` - остановка тактового генератора.

  Арифметические операции:
  - `ADD { e1, e2 }` – положить на стек результат операции сложения e1 + e2.
  - `SUB { e1, e2 }` – положить на стек результат операции вычитания e1 – e2.
  - `MUL { e1, e2 }` – положить на стек результат операции умножения e1 * e2.
  - `DIV { e1, e2 }` – положить на стек результат операции деления e1 / e2.
  - `MOD { e1, e2 }` – положить на стек результат операции взятия остатка e1 % e2.
  - `INC { element }` – увеличить значение top of the stack на 1.
  - `DEC { element }` – уменьшить значение top of the stack на 1. 

- `SWAP { e1, e2 }` – поменять на стеке два элемента местами.
- `OVER { e1 } [ e2 ]` – дублировать первый элемент на стеке через второй.
  Если в стеке только 1 элемент – поведение не определено.
- `in { port }`  - получить данные из внешнего устройства по указанному порту.
- `out { port, value }` - отправить данные во внешнее устройство по указанному порту.

 ## Кодирование инструкций

  Машинный код преобразуется в список JSON,
  где один элемент списка — это одна инструкция.
  Индекс инструкции в списке – адрес этой инструкции в памяти.
  Пример машинного слова:
    
```json
[
    {
        "opcode": "push",
        "arg": 5,
        "term": [
            1,
            5,
            "push 5",
            "]"
        ]
    }
]
```
 - `opcode` -- строка с кодом операции;
 - `arg` -- аргумент (может отсутствовать);
 - `term` -- информация о связанном месте в исходном коде (если есть).

  Типы данных в модуле [isa](./processor/isa.py), где:

- `Opcode` -- перечисление кодов операций;
- `Term` -- структура для описания значимого фрагмента кода исходной программы.


## Транслятор

 Интерфейс командной строки: `translator.py <input_file> <target_file>`

 Реализовано в модуле: [translator](translator.py)

 Этапы трансляции (функция `translate`):

1) Генерация машинного кода без адресов переходов
   и расчёт значений меток перехода.  

2) Подстановка меток перехода в инструкции.

## Модель процессора

Интерфейс командной строки: `machine.py <machine_code_file> <input_file>`

Реализована в модуле [machine](/processor/machine.py).

### DataPath

![DataPath](/resources/DataPath.png)

Реализован в классе `DataPath` в [machine.py](/processor/machine.py)

Управляющие сигналы описаны в модуле [signals](processor/signals.py)

- `DS_PUSH` - защелкнуть вершину стека данных во второй элемент стека данных;
- `DS_POP` - убрать второй элемент из стека данных;
- `LATCH_TOS` - защелкнуть выбранное значение в вершину стека данных:
  - `LATCH_TOS_MEM_OUT` - - защелкнуть значение из памяти
  - `LATCH_TOS_FROM_ALU` - защелкнуть значение из АЛУ
  - `LATCH_TOS_FROM_STACK` - защелкнуть значение второго элемента стека данных
  - `LATCH_TOS_INPUT` - защелкнуть значение из IO контроллера
  - `LATCH_TOS_BR` - защелкнуть значение из буферного регистра
- `LATCH_AR`
  - `LATCH_ADDR_PC` - защелкнуть значение из счетчика команд
  - `LATCH_ADDR_TOS` - защелкнуть значение из вершины стека
- `WRITE` - записать в память по адресу из AR второй элемент стека данных
- `OUT` - отправить второй элемент стека данных на внешнее устройство по порту,
указанному в вершине стека данных

Флаги:
- `zero (z)` - проверка вершины стека на ноль

### ControlUnit

![ControlUnit](/resources/ControlUnit.png)

Реализован в классе `ContolUnit` в [machine.py](processor/machine.py)

- Hardwired (реализовано полностью на Python).
- Метод decode_and_execute_instruction моделирует выполнение полного цикла инструкции.
- tick_counter необходим для многотактовых инструкций.

    Управляющие сигналы описаны в модуле [signals](processor/signals.py):
  - `latch_program_counter` - защелкнуть выбранное значение в счетчик команд:
    - `PC_NEXT` - защелкнуть инкрементированное значение счетчика команд
    - `PC_JMP` - защелкнуть значение из вершины стека данных
    - `PC_JZ` - защелкнуть значение из второго элемента стека данных если флаг zero (Z) равен 1, иначе защелкнуть инкрементированное значение из счетчика команд
    - `PC_RS` - защелкнуть значение из вершины стека возврата
  - `RS_PUSH` - защелкнуть в стеке возврата инкрементированное значение счетчика команд
  - `RS_POP` - убрать элемент из стека возврата

    
- Цикл симуляции осуществляется в функции `simulation`.
- Шаг моделирования соответствует одной инструкции с выводом состояния в журнал.
- Для журнала состояний процессора используется стандартный модуль `logging`.
- Количество инструкций для моделирования лимитировано.
- Остановка моделирования осуществляется при:
    - превышении лимита количества выполняемых инструкций;
    - исключении `EOFError` -- если нет данных для чтения из порта ввода;
    - исключении `StopIteration` -- если выполнена инструкция `hlt`.

## Тестирование

Тестирование выполняется при помощи golden test-ов.

Настройки golden тестирования находятся в [golden_test.py](golden_test.py).

Конфигурация golden test-ов лежит в [golden_tests](golden_tests)

Тестовое покрытие:

- `cat` – повторяет поток ввода на вывод
- `hello_world` – печатает на выход “Hello, world!”
- `hello_username` – печатает на выход приветствие пользователя
- `prob1` – сумма чисел от 1 до 1000, кратные 3 либо 5.

Запустить тесты: 
```shell
poetry run pytest . -v
```

Обновить конфигурацию golden-тестов: 
```shell
poetry run pytest . -v --update-goldens
```

### CI

CI при помощи Github Actions настроен в [файле ci.yml](.github/workflows/ci.yml)

``` yaml
name: csa-lab3

on:
  push:
    branches:
      - master
    paths:
      - ".github/workflows/*"
      - "python/**"
  pull_request:
    branches:
      - master
    paths:
      - ".github/workflows/*"
      - "python/**"


jobs:
  golden:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.9

      - name: Install dependencies
        run: |
          python3 -m pip install --upgrade pip
          pip3 install poetry
          poetry install

      - name: Run tests and collect coverage
        run: |
          poetry run coverage run -m pytest .
          poetry run coverage report -m
        env:
          CI: true

  ruff:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.9

      - name: Install dependencies
        run: |
          python3 -m pip install --upgrade pip
          pip3 install poetry
          poetry install

      - name: Check code formatting with Ruff
        run: |
          poetry run ruff format --check . --exclude uarch.py

      - name: Run Ruff linters
        run: |
          poetry run ruff check .

  mypy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.9

      - name: Install dependencies
        run: |
          python3 -m pip install --upgrade pip
          pip3 install poetry
          poetry install

      - name: Check static typing with mypy
        run: |
          poetry run mypy .
```

Использованы следующие команды:

- `poetry` - управления зависимостями Python;
- `coverage` - формирование отчёта об уровне покрытия исходного кода;
- `pytest` - программа для запуска тестов;
- `ruff` - линтер и форматтер;
- `mypy` - проверка статической типизации

Тестовые процессы:

- `golden` - запуск golden-тестов
- `ruff` - запуск линтера и проверки форматирования `ruff`
- `mypy` - запуск проверки статической типизации `mypy`

## Пример использования

Пример алгоритма [cat.asm](asm_programs/cat.asm)
- Ввод: `Hello, world!`

- Вывод:
``` commandline
DEBUG:root:TICK:   0 PC:   0 ADDR:   0 MEM_OUT: 3 DS: [] TOS: 0 	push 3  ('push start'@1:0)
DEBUG:root:TICK:   3 PC:   1 ADDR:   0 MEM_OUT: 3 DS: [0] TOS: 3 	jmp  ('jmp'@1:0)
DEBUG:root:TICK:   6 PC:   3 ADDR:   0 MEM_OUT: 3 DS: [] TOS: 0 	push 2  ('push port'@3:0)
DEBUG:root:TICK:   9 PC:   4 ADDR:   3 MEM_OUT: 2 DS: [0] TOS: 2 	load  ('load'@4:0)
DEBUG:root:TICK:  11 PC:   5 ADDR:   2 MEM_OUT: 1 DS: [0] TOS: 1 	in  ('in'@5:0)
DEBUG:root:TICK:  12 PC:   6 ADDR:   2 MEM_OUT: 1 DS: [0] TOS: 13 	dup  ('dup'@6:0)
DEBUG:root:TICK:  14 PC:   7 ADDR:   2 MEM_OUT: 1 DS: [0, 13] TOS: 13 	push 2  ('push port'@7:0)
DEBUG:root:TICK:  17 PC:   8 ADDR:   7 MEM_OUT: 2 DS: [0, 13, 13] TOS: 2 	load  ('load'@8:0)
DEBUG:root:TICK:  19 PC:   9 ADDR:   2 MEM_OUT: 1 DS: [0, 13, 13] TOS: 1 	out  ('out'@9:0)
DEBUG:root:Output: writing 13 on port 1
DEBUG:root:TICK:  23 PC:  10 ADDR:   2 MEM_OUT: 1 DS: [0] TOS: 13 	dup  ('dup'@10:0)
DEBUG:root:TICK:  25 PC:  11 ADDR:   2 MEM_OUT: 1 DS: [0, 13] TOS: 13 	push 27  ('push    break'@11:0)
DEBUG:root:TICK:  28 PC:  12 ADDR:  11 MEM_OUT: 27 DS: [0, 13, 13] TOS: 27 	swap  ('swap'@12:0)
DEBUG:root:TICK:  32 PC:  13 ADDR:  11 MEM_OUT: 27 DS: [0, 13, 27] TOS: 13 	jz  ('jz'@13:0)
DEBUG:root:TICK:  36 PC:  14 ADDR:  11 MEM_OUT: 27 DS: [0] TOS: 13 	push 2  ('push port'@15:0)
DEBUG:root:TICK:  39 PC:  15 ADDR:  14 MEM_OUT: 2 DS: [0, 13] TOS: 2 	load  ('load'@16:0)
DEBUG:root:TICK:  41 PC:  16 ADDR:   2 MEM_OUT: 1 DS: [0, 13] TOS: 1 	in  ('in'@17:0)
DEBUG:root:TICK:  42 PC:  17 ADDR:   2 MEM_OUT: 1 DS: [0, 13] TOS: 72 	push 2  ('push port'@18:0)
DEBUG:root:TICK:  45 PC:  18 ADDR:  17 MEM_OUT: 2 DS: [0, 13, 72] TOS: 2 	load  ('load'@19:0)
DEBUG:root:TICK:  47 PC:  19 ADDR:   2 MEM_OUT: 1 DS: [0, 13, 72] TOS: 1 	out  ('out'@20:0)
DEBUG:root:Output: writing `H` (72) on port 1

...

INFO:root:output_buffer: 'Hello, world!'
Hello, world!
instr_counter:  180 ticks: 498
```

## Пример тестирования исходного кода
``` commandline
 poetry run pytest . -v                 
C:\Users\slava\AppData\Local\Programs\Python\Python39\lib\site-packages\pytest_golden\plugin.py:53: GoldenTestUsageWarning: Add 'enable_assertion_pass_hook=true' to pytest.ini for safer usage of pytest-golden.
  warnings.warn(
================================================================================= test session starts ================================================================================= 
platform win32 -- Python 3.9.13, pytest-8.2.2, pluggy-1.5.0 -- C:\Users\slava\AppData\Local\Programs\Python\Python39\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\slava\PycharmProjects\csa-lab3
configfile: pyproject.toml
plugins: golden-0.2.2
collected 4 items                                                                                                                                                                      

golden_test.py::test_translator_and_machine[golden_tests/cat_golden.yml] PASSED                                                                                                  [ 25%]
golden_test.py::test_translator_and_machine[golden_tests/hello_golden.yml] PASSED                                                                                                [ 50%]
golden_test.py::test_translator_and_machine[golden_tests/hello_username_golden.yml] PASSED                                                                                       [ 75%]
golden_test.py::test_translator_and_machine[golden_tests/prob1_golden.yml] PASSED                                                                                                [100%]

================================================================================== 4 passed in 2.36s ================================================================================== 
```

## Статистика

```
| ФИО             | алг            | LoC | code инстр. | инстр. | такт.  |
+-----------------+----------------+-----+-------------+--------+--------+
| Подольский В.И. | hello_world    | 36  | 44          | 205    | 600    |
| Подольский В.И. | cat            | 33  | 28          | 180    | 498    |
| Подольский В.И. | hello_username | 99  | 139         | 725    | 2133   |
| Подольский В.И. | prob1          | 47  | 39          | 20859  | 63174  |
```

