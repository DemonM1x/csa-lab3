data:
    port: 1
    hello: "Hello, world!"

start:
                push hello          ; [hello_addr]
                load                ; [len]
                dup                 ; [len, len]
                push port           ; [len, len, port_addr]
                load                ; [len, len, port]
                out                 ; [len]
                dup                 ; [len, len]
                push exit           ; [len, len, exit]
                swap                ; [len, exit, len]
                jz                  ; [len]
                push hello          ; [len, hello_addr]
loop:
    inc                 ; [len, hello_addr++]
    dup                 ; [len, hello_addr, hello_addr]
    load                ; [len, hello_addr, chr]
    push port           ; [len, hello_addr, chr, port_addr]
    load                ; [len, hello_addr, chr, port]
    out                 ; [len, hello_addr]
    ; len--, hlt if len == 0
    swap                ; [hello_addr, len]
    dec                 ; [hello_addr, len--]
    dup                 ; [hello_addr, len, len]
    push    exit       ; [hello_addr, len, len, exit]
    swap                ; [hello_addr, len, exit, len]
    jz                  ; [hello_addr, len]
    ; loop
    swap                ; [len, hello_addr]
    push    loop        ; [len, hello_addr, loop_addr]
    jmp                 ; [len, hello_addr]
exit:
    hlt                ;
