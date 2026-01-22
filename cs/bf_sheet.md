This is Brainfuck chip(nearly equiv 8bit computer)

Not like ordinary [8bit computer](https://en.wikipedia.org/wiki/MOS_Technology_6502), I over simplify the design. There's no TCU(timing control unit), and run static fetch-decode-execute cycle. To make it possible, I break down BF code piece, for instance '>'=PTR_INC+READ or '+'=REG_INC+WRITE. In practical, there are two 8bit register and RAM256x8; first register for holding ptr position, second for tape value. In conclusion, this chip can perform 8 ops listed below.

| MNEMONIC | OPCODE | BF                 |
| -------- | ------ | ------------------ |
| INIT     | 000    | NONE               |
| PTR_INC  | 001    | '>'(without read)  |
| PTR_DEC  | 010    | '<'(without read)  |
| REG_INC  | 011    | '+'(without write) |
| REG_DEC  | 100    | '-'(without write) |
| READ     | 101    | NONE               |
| WRITE    | 110    | NONE               |
| JUMP     | 111    | '[', ']'           |

So does the following shift 1 ptr code(`@++[->+<]`) be like.

in MNEMONIC

```
000: INIT ALWAYS 0
001: REG_INC ALWAYS 0
002: WRITE ALWAYS 0
003: REG_INC ALWAYS 0
004: WRITE ALWAYS 0
005: JUMP IF_ZERO 14
006: PTR_INC ALWAYS 0
007: READ ALWAYS 0
008: REG_INC ALWAYS 0
009: WRITE ALWAYS 0
010: PTR_DEC ALWAYS 0
011: READ ALWAYS 0
012: REG_DEC ALWAYS 0
013: WRITE ALWAYS 0
014: JUMP IF_NONZERO 5
```

in Binary

```
0000000000000000 ; (000)(11)(xxx)(22222222)
0110000000000000 ; ㄴ 0: OPCODE
1100000000000000 ; ㄴ 1: COND (00: always / 01: IF_ZERO / 10: IF_NZERO)
0110000000000000 ; ㄴ 2: ADDR (for `JUMP`)
1100000000000000
1110100000001110 ; JUMP IF_ZERO TO 14
0010000000000000
1010000000000000
0110000000000000
1100000000000000
0100000000000000
1010000000000000
1000000000000000
1100000000000000
1111000000000101
```
