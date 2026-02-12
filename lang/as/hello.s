/*
--- AT&T IA-32 (x64) assembly ---
    Yooooooooooooooooooooooo
*/

# registers
#   eax, ebx, ecx, edx, edi, esi, esp, ebp, (eip)
#   ㄴ        universal       ㄱ  ㄴstackㄱ   ㄴ PC

# push S
#   sub $4, %esp
#   mov  S, (%esp)
# pop S
#   mov (%esp), S
#   add $4, (%esp)

# leave        -> frame 원상태
# call <add r> -> push %eip / move addr %eip
# ret          -> pop  %eip

# Caller-saved : EAX, ECX, EDX
# Callee-saved : EBX, ESI, EDI, EBP

.section .text
.global _start

/*
int add(int a, int b) {
    return a+b;
}
*/
_add:
    # callee saved
    push  %ebp
    mov   %esp, %ebp

    # load a from 0xc(%ebp)
    movl  0x8(%ebp), %eax
    # a + b -> %eax
    add   0xc(%ebp), %eax

    leave
    ret

/*
int max(int a, int b)
    return a > b ? a : b;
*/
_max:
    push  %ebp
    mov   %esp, %ebp
    mov   0xc(%ebp), %eax # b
    // cmp   %eax, 0x8(%ebp) # a
    // jle   .ldone
    // mov   0x8(%ebp), %eax
// .ldone:
    // leave
    // ret
    // another way
    cmovle 0x8(%ebp), %eax
    leave
    ret

/*
int incre(int *x) {
    if (x != NULL) {
        return (*x)++;
    }
    else {
        return 1;
    }
    // x ? (*x)++ : 1;
}
*/
_inc:
    push  %ebp
    mov   %esp, %ebp
    cmpl  $0x0, 0x8(%ebp)
    je    .if_null   
    mov   0x8(%ebp), %eax
    mov   (%eax), %eax
    lea   0x1(%eax), %ecx
    mov   0x8(%ebp), %edx
    mov   %ecx, (%edx)
    jmp   .done
.if_null:
    movl  $0x1, %eax
.done:
    leave
    ret

/*
int sumUp(int n) {
    int total = 0;
    int i = 1;

    while (i <= n) {
        total += i;
        i += 1;
    }
    return total;
}
*/
_sumUp:
    push  %ebp
    mov   %esp, %ebp

    addl  $0x10, %esp
    movl  $0x0, 0x4(%esp)
    movl  $0x1, 0x8(%esp)

    jmp   .condition
.loop:
    mov   0x4(%esp), %eax
    add   0x8(%esp), %eax
    mov   %eax, 0x4(%esp)
    mov   0x8(%esp), %eax
    lea   0x1(%eax), %eax
    mov   %eax, 0x8(%esp)
.condition:
    mov   0x8(%ebp), %eax # n
    cmp   0x8(%esp), %eax # i
    jge   .loop

    mov   0x4(%esp), %eax # move total

    subl  $0x10, %esp
    leave
    ret

_start:
    #  basic
    push  %ebp
    mov   %esp, %ebp

    // push  $0x3 # b
    // push  $0x2 # a
    // call  _max

    // push  $0x1
    // push  %esp # *i
    // call  _inc

    push  $0xa
    call  _sumUp

    pop   %ebp

exit:
    #  Exit syscall
    movl  $1, %eax
    xor  %ebx, %ebx
    int  $0x80;
