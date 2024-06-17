# Архитектура компьютера. Лабораторная работа №3
- Подольский Вячеслав Ильич, P3220
- asm| stack | neum | hw | instr | stuct | stream | port | pstr | prob1 
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

- В коде данные объявляются в специальном разделе `data`. в которой могут быть 
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
|  n  : HLT                   |
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




