data:
    port: 1
start:
        push port
        load
        in                  ; [len]
        dup                 ; [len, len]
        push port
        load
        out                 ; [len]
        dup                 ; [len, len]
        push    break       ; [len, len, break]
        swap                ; [len, break, len]
        jz                  ; [len]
loop:
        push port
        load
        in                  ; [len, chr]
        push port
        load
        out                 ; [len]
        ; len--, halt if len == 0
        dec                 ; [len--]
        dup                 ; [len, len]
        push    break       ; [len, len, break]
        swap                ; [len, break, len]
        jz                  ; [len]

        ; loop
        push    loop        ; [len, loop]
        jmp                 ; [len]
break:
        hlt