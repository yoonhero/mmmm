# code = """<<[[->+>+<
# <]>------<
# [>]>++><--
# [->[--]]<]
# --+->>[[<+
# >-+->-<]<<
# +->][<[>>>
# >-<][]>[>>
# +--<<<>>>>
# <<-]+<>>>]"""

code = """[>]+[+<
><[--><
][]>[<+
+->-]--
[-[][]-
+><-]<>
<<+-->]"""

code = """>[-
<->
><]"""

N = len(code.split("\n"))
transposed_code = ["".join([code.split("\n")[i][j] for i in range(N)]) for j in range(N)]
code = code.replace("\n", "")
print(code, "".join(transposed_code))
print("".join(transposed_code) == code)
# code = "[[->+>+<<]>------[->[-]]<]>>[[-<+>]<<>]"

tape = [0]*128
def test(code, tape):
    tape = tape[:]
    pc = 0
    ptr = 0
    while pc < len(code):
        # print(pc, tape[:10])
        char = code[pc]
        match char:
            case "<": ptr = max(0, ptr-1)
            case ">": ptr += 1
            case "+": tape[ptr] += 1
            case "-": tape[ptr] = max(0, tape[ptr]-1)
            case "]":
                if tape[ptr] != 0:
                    local = 1
                    while local != 0:
                        pc -= 1
                        if code[pc] == "[":
                            local -= 1
                        elif code[pc] == "]":
                            local += 1
            case "[":
                if tape[ptr] == 0:
                    local = 1
                    while local != 0:
                        pc += 1
                        if code[pc] == "[":
                            local += 1
                        elif code[pc] == "]":
                            local -= 1
        pc += 1 
    # print(f"TEST {cin}: {tape[0:10]}")
    return tape

# for i in range(220):
#     if i % 7 != test("".join(transposed_code), i):
#         print(i, tape[:10])

tape = list(range(51))
tape[0] = 100
for i in range(1,50):
    tape[i] = 0
    print(test(code, tape)[0])
    tape[i] = i
