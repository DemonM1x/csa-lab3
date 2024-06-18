data:
    port: 1
    hello: "Hello, world!"

start:
                push hello          ; hello_addr
                load
                dup
                push port
                load
                out
                dup
                push exit
                swap
                jz
                push hello
loop:
    inc                 ; [len, hello_addr++]
    dup                 ; [len, hello_addr, hello_addr]
    load                ; [len, hello_addr, chr]
    push port
    load
    out                 ; [len, hello_addr]
    ; len--, hlt if len == 0
    swap                ; [hello_addr, len]
    dec                 ; [hello_addr, len--]
    dup                 ; [hello_addr, len, len]
    push    exit       ; [hello_addr, len, len, break]
    swap                ; [hello_addr, len, break, len]
    jz                  ; [hello_addr, len]
    ; loop
    swap                ; [len, hello_addr]
    push    loop        ; [len, hello_addr, loop_addr]
    jmp                 ; [len, hello_addr]
exit:
                hlt                ;
