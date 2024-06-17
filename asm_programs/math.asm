; math

data:
    a:      3
    b:      -5
    c:      2

      ; (a + b) * c
start:
    push    c
    load
    push    b
    load
    push    a
    load
    add
    mul
    out
    hlt
