#!/usr/bin/env python
rom_words = 256
def make_rom(rom_words=256):
    rom = bytearray([0x00] * (rom_words*2)) # 256x16 ROM
    return rom
endian = "big" # (d0<<8)+d1
MNEMONIC_TO_OPCODE = {
    "PTR_INC": 0b001,
    "PTR_DEC": 0b010,
    "REG_INC": 0b011,
    "REG_DEC": 0b100,
    "READ": 0b101,
    "WRITE": 0b110,
    "JUMP": 0b111, # jump
    "INIT": 0b000
}
COND_TO_OPCODE = {
    "ALWAYS": 0b00,
    "IF_ZERO": 0b01,
    "IF_NONZERO": 0b10
}
OPCODE_TO_MNEMONIC = {v:k for k, v in MNEMONIC_TO_OPCODE.items()}
OPCODE_TO_COND = {v:k for k, v in COND_TO_OPCODE.items()}

def write_word(mem, addr, word):
    mem[2*addr:2*addr+2] = word.to_bytes(2, endian)
def read_word(mem, addr):
    word = int.from_bytes(mem[2*addr:2*addr+2], endian)
    return f"{word:016b}"

WORD_BITS = 16
OP_BITS = 3
IMM_BITS = 8
COND_BITS = 2
OP_SHIFT = WORD_BITS - OP_BITS
COND_SHIFT = OP_SHIFT - COND_BITS
COND_MASK = (1<<COND_BITS)-1
IMM_MASK = (1<<IMM_BITS)-1
def encode_asm(asm_inst, cond="ALWAYS", j_addr=0):
    return (MNEMONIC_TO_OPCODE[asm_inst]<<OP_SHIFT) + (COND_TO_OPCODE[cond]<<COND_SHIFT) + j_addr # 000xxxxx11111111 [inst][unused][j_addr]
def decode_asm(opcode):
    inst = opcode>>OP_SHIFT
    cond = (opcode>>COND_SHIFT) & COND_MASK
    j_addr = opcode & IMM_MASK # 0xFF
    return f"{OPCODE_TO_MNEMONIC[inst]} {OPCODE_TO_COND[cond]} {j_addr}"
def emit(mem, addr, asm_inst, cond="ALWAYS", j_addr=0):
    asm = encode_asm(asm_inst, cond=cond, j_addr=j_addr)
    write_word(mem, addr, asm)
    return addr + 1

def compile(program):
    addr = 0
    rom = make_rom()
    jump_stack = []
    
    for inst in program:
        asms = []
        match inst:
            case "@":
                asms = ["INIT"]
            case ">":
                asms = ["PTR_INC", "READ"]
            case "<":
                asms = ["PTR_DEC", "READ"]
            case "+":
                asms = ["REG_INC", "WRITE"]
            case "-":
                asms = ["REG_DEC", "WRITE"]
            case "[":
                jump_stack.append(addr)
                addr += 1
            case "]":
                jump_start = jump_stack.pop(-1)
                emit(rom, jump_start, "JUMP", cond="IF_ZERO", j_addr=addr)
                addr = emit(rom, addr, "JUMP", cond="IF_NONZERO", j_addr=jump_start)
            case _: pass
        for asm in asms:
            addr = emit(rom, addr, asm)
    return rom

# test = "@++[>+<-]" # copy
# test = "@+><"
# test = "@+[>+]" # fill 1
# test = "@++++[>+>+<<--]>>[-<<+>>]" # duplicate
test = "@+>+[[-<+<+>>]<[[->+<]<]>>>]" # fibonacii
rom = compile(test)
lines = []
for addr in range(256):
    word = read_word(rom, addr)
    lines.append(word)
    print(f"{addr:03d}: {decode_asm(int(word, 2))}")
with open("bf.mem", "w") as f:
    f.write("\n".join(lines))