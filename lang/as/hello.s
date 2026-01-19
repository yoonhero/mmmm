// > nasm -f macho64 helloworld.asm -o Main.o
// > clang -arch x86_64 Main.o -o hello
// throw it! use arm!
.global _start
.align 4

_start:
    mov     w0, #0
    ret     
