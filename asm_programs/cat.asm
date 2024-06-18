data:
    port: 1
start:
        push port           ; [port_addr]
        load                ; [port]
        in                  ; [len]
        dup                 ; [len, len]
        push port           ; [len, len, port_addr]
        load                ; [len, len, port]
        out                 ; [len]
        dup                 ; [len, len]
        push    break       ; [len, len, break]
        swap                ; [len, break, len]
        jz                  ; [len]
loop:
        push port           ; [len, port_addr]
        load                ; [len, port]
        in                  ; [len, chr]
        push port           ; [len, chr, port_addr]
        load                ; [len, chr, port]
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