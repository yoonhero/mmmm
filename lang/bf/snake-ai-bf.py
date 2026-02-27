# BF on beef interpreter
# -> unbound tape length
# -> tape value is signed int8(-128...127)
from turing_and_bf import *
from make_snake_bf import *

REG0 = REG_AREA
REG1 = REG_AREA+1
REG2 = REG_AREA+2
REG3 = REG_AREA+3

ZERO = alloc_table["memory"]
SRAM = alloc_table["memory"]+1
OBV = alloc_table["memory"]+4
MEMORY = alloc_table["memory"]+9

#### MLP ####
# ADD = ((reg0)) reg1
add_x_y = lambda x: lambda y: safe_load_xy_reg0_reg1(x)(y)+go_work_back(REG1)('[-<+>]')
# MUL = reg0 reg1 ((reg2)) reg3
# ab-8 = AB +64 + 8(A+B) -8
mul_x_y = lambda x: lambda y: safe_load_xy_reg0_reg1(x)(y)+go_work_back(REG0)('[->[->+>+<<]>>[-<<+>>]<<<]')

int4_add_x_y = lambda x: lambda y: add_x_y(x)(y)+go_sub_n(REG0)(8)
# ab+z = (a+z)(b+z)-(A+B)z+z^2+z
# ab+8 = AB-(A+B)8+72
# INT4_MUL = reg0 reg1 ((reg2)) reg3
int4_mul_x_y = lambda x: lambda y: mul_x_y(x)(y)+go_add_n(REG2)(72)+move_a_to_b(REG2)(SRAM)+add_x_y(x)(y)+move_a_to_b(SRAM)(REG2)+go_add_n(REG1)(8)+go_work_back(REG0)('[->[->->+<<]>>[-<<+>>]<<<]')

relu = lambda x: if_x_geq_y(ZERO)(x)(go_work_back(MEMORY)(reset+add_n(8)))
clamp = lambda x: if_x_geq_a(x)(15)(go_work_back(x)(reset+add_n(15)))

int4_mul = lambda x: lambda y: lambda dest: int4_mul_x_y(x)(y)+move_a_to_b(REG2)(dest)

# a0~a3 / b0~b3 -> contiguous memory allocation
# c0~c3 must be initialized
matmul2x2 = lambda a_start: lambda a_middle: lambda b_start: lambda b_middle: lambda c_start: lambda c_middle: int4_mul(a_start)(b_start)(c_start)+int4_mul(a_start+1)(b_middle)(c_start)+\
    int4_mul(a_start)(b_start+1)(c_start+1)+int4_mul(a_start+1)(b_middle+1)(c_start+1)+\
    int4_mul(a_middle)(b_start)(c_middle)+int4_mul(a_middle+1)(b_middle)(c_middle)+\
    int4_mul(a_middle)(b_start+1)(c_middle+1)+int4_mul(a_middle+1)(b_middle+1)(c_middle+1)+\
    go_sub_n(c_start)(8)+go_sub_n(c_start+1)(8)+go_sub_n(c_middle)(8)+go_sub_n(c_middle+1)(8)+\
    clamp(c_start)+clamp(c_start+1)+clamp(c_middle)+clamp(c_middle+1)

# matmul4x4 = lambda a_start: lambda b_start: lambda c_start: 
matmul4x4 = lambda a_start: lambda b_start: lambda c_start: \
    matmul2x2(a_start)(a_start+4)(b_start)(b_start+4)(c_start)(c_start+4) + \
    matmul2x2(a_start+2)(a_start+6)(b_start+8)(b_start+12)(c_start)(c_start+4) + \
    matmul2x2(a_start)(a_start+4)(b_start+2)(b_start+6)(c_start+2)(c_start+6) + \
    matmul2x2(a_start+2)(a_start+6)(b_start+10)(b_start+14)(c_start+2)(c_start+6) + \
    matmul2x2(a_start+8)(a_start+12)(b_start)(b_start+4)(c_start+8)(c_start+12) + \
    matmul2x2(a_start+10)(a_start+14)(b_start+8)(b_start+12)(c_start+8)(c_start+12) + \
    matmul2x2(a_start+8)(a_start+12)(b_start+2)(b_start+6)(c_start+10)(c_start+14) + \
    matmul2x2(a_start+10)(a_start+14)(b_start+10)(b_start+14)(c_start+10)(c_start+14) + \
    go_sub_n(c_start)(8)+go_sub_n(c_start+1)(8)+go_sub_n(c_start+2)(8)+go_sub_n(c_start+3)(8) + \
    go_sub_n(c_start+4)(8)+go_sub_n(c_start+5)(8)+go_sub_n(c_start+6)(8)+go_sub_n(c_start+7)(8) + \
    go_sub_n(c_start+8)(8)+go_sub_n(c_start+9)(8)+go_sub_n(c_start+10)(8)+go_sub_n(c_start+11)(8) + \
    go_sub_n(c_start+12)(8)+go_sub_n(c_start+13)(8)+go_sub_n(c_start+14)(8)+go_sub_n(c_start+15)(8) + \
    clamp(c_start)+clamp(c_start+1)+clamp(c_start+2)+clamp(c_start+3) + \
    clamp(c_start+4)+clamp(c_start+5)+clamp(c_start+6)+clamp(c_start+7) + \
    clamp(c_start+8)+clamp(c_start+9)+clamp(c_start+10)+clamp(c_start+11) + \
    clamp(c_start+12)+clamp(c_start+13)+clamp(c_start+14)+clamp(c_start+15)

linear4x4_no_bias = lambda w_start: lambda b_start: lambda c_start: \
    int4_mul(w_start)(b_start)(c_start) + \
    int4_mul(w_start+1)(b_start+1)(c_start)+go_sub_n(c_start)(8) + \
    int4_mul(w_start+2)(b_start+2)(c_start)+go_sub_n(c_start)(8) + \
    int4_mul(w_start+3)(b_start+3)(c_start)+go_sub_n(c_start)(8) + \
    int4_mul(w_start+4)(b_start)(c_start) + \
    int4_mul(w_start+5)(b_start+1)(c_start)+go_sub_n(c_start)(8) + \
    int4_mul(w_start+6)(b_start+2)(c_start)+go_sub_n(c_start)(8) + \
    int4_mul(w_start+7)(b_start+3)(c_start)+go_sub_n(c_start)(8) + \
    int4_mul(w_start+8)(b_start)(c_start) + \
    int4_mul(w_start+9)(b_start+1)(c_start)+go_sub_n(c_start)(8) + \
    int4_mul(w_start+10)(b_start+2)(c_start)+go_sub_n(c_start)(8) + \
    int4_mul(w_start+11)(b_start+3)(c_start)+go_sub_n(c_start)(8) + \
    int4_mul(w_start+12)(b_start)(c_start) + \
    int4_mul(w_start+13)(b_start+1)(c_start)+go_sub_n(c_start)(8) + \
    int4_mul(w_start+14)(b_start+2)(c_start)+go_sub_n(c_start)(8) + \
    int4_mul(w_start+15)(b_start+3)(c_start)+go_sub_n(c_start)(8) + \
    clamp(c_start)+clamp(c_start+1)+clamp(c_start+2)+clamp(c_start+3)

bias_add = lambda dest: lambda bias: safe_load_data(bias)(REG0)+move_a_to_b(REG0)(dest)
linear4x4_bias = lambda w_start: lambda x_start: lambda bias_start: lambda result_start: \
    linear4x4_no_bias(w_start)(x_start)(result_start)+\
    bias_add(result_start)(bias_start)+bias_add(result_start+1)(bias_start+1)+\
    bias_add(result_start+2)(bias_start+2)+bias_add(result_start+3)(bias_start+3)

# w/a/s/d : 1/2/3/4
maximum = go_work_back(OBV+4)(reset) + \
    if_x_geq_y(OBV)(OBV+1)(if_x_geq_y(OBV)(OBV+2)(if_x_geq_y(OBV)(OBV+3)(go_add_n(OBV+4)(1)))) + \
    if_x_geq_y(OBV+1)(OBV)(if_x_geq_y(OBV+1)(OBV+2)(if_x_geq_y(OBV+1)(OBV+3)(go_add_n(OBV+4)(2)))) + \
    if_x_geq_y(OBV+2)(OBV)(if_x_geq_y(OBV+2)(OBV+1)(if_x_geq_y(OBV+2)(OBV+3)(go_add_n(OBV+4)(3)))) + \
    if_x_geq_y(OBV+3)(OBV)(if_x_geq_y(OBV+3)(OBV+1)(if_x_geq_y(OBV+3)(OBV+2)(go_add_n(OBV+4)(4))))

sub = '[-<->]'
# result on SRAM
mod8 = lambda x: safe_load_data(x)(SRAM) + if_x_geq_a(SRAM)(8)(go_sub_n(SRAM)(8)+\
                                  if_x_geq_a(SRAM)(8)(go_sub_n(SRAM)(8)+\
                                    if_x_geq_a(SRAM)(8)(go_sub_n(SRAM)(8)+\
                                        if_x_geq_a(SRAM)(8)(go_sub_n(SRAM)(8)+\
                                            if_x_geq_a(SRAM)(8)(go_sub_n(SRAM)(8)+\
                                                if_x_geq_a(SRAM)(8)(go_sub_n(SRAM)(8)+
                                                    if_x_geq_a(SRAM)(8)(go_sub_n(SRAM)(8))))))))
# result on REG1
div8 = lambda x: mod8(x)+safe_load_data(x)(REG0)+move_a_to_b(SRAM)(REG1)+sub+\
    '<[-------->+<]'
# result on REG0
int4_sub = lambda x: lambda y: safe_load_xy_reg0_reg1(x)(y)+go_work_back(REG1)(sub)+go_add_n(REG0)(8)
get_obv = if_x_eq_a(INPUT_AREA)(1)(go_work_back(OBV+3)(go_add_n(9)))+\
    if_x_eq_a(INPUT_AREA)(2)(go_work_back(OBV+2)(go_add_n(7)))+\
    if_x_eq_a(INPUT_AREA)(3)(go_work_back(OBV+3)(go_add_n(7)))+\
    if_x_eq_a(INPUT_AREA)(4)(go_work_back(OBV+2)(go_add_n(9)))+\
    mod8(APPLE_AREA)+move_a_to_b(SRAM)(SRAM+1)+\
    mod8(INPUT_AREA)+\
    int4_sub(SRAM+1)(SRAM)+move_a_to_b(REG0)(OBV)+\
    div8(INPUT_AREA)+move_a_to_b(REG1)(SRAM)+\
    div8(APPLE_AREA)+move_a_to_b(REG1)(SRAM+1)+\
    int4_sub(SRAM+1)(SRAM)+move_a_to_b(REG0)(OBV+1)

W0 = MEMORY
B0 = MEMORY+16
W1 = MEMORY+20
B1 = MEMORY+36
W2 = MEMORY+40
B2 = MEMORY+56
W3 = MEMORY+60
B3 = MEMORY+76
Y = MEMORY+80

move_YtoX = safe_move_a_to_b(Y)(OBV)+\
    safe_move_a_to_b(Y+1)(OBV+1)+\
    safe_move_a_to_b(Y+2)(OBV+2)+\
    safe_move_a_to_b(Y+3)(OBV+3)

predict = linear4x4_bias(W0)(OBV)(B0)(Y)+move_YtoX + \
    maximum + safe_move_a_to_b(OBV+4)(INPUT_AREA)

work_script += get_obv
work_script += predict

main_script = loop(work_script)
w0 = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
b0 = [-1, 0, -1, 0]
for i in range(8):
    init_snake += go_add_n(W0+i)(w0[i])
for i in range(4):
    init_snake += go_add_n(B0+i)(b0[i])
script = init_snake + main_script

bf_script = optimize(script)

with open("test.bf", "w") as f:
    print(f"Length: {len(bf_script)}\n")
    f.write(optimize(bf_script))

# test_script = go_add_n(ZERO)(8)
# test_script += go_add_n(IF_AREA+3)(1) # if trigger flag

# # test_script += go_add_n(MEMORY)(8+4)
# # test_script += int4_mul_x_y(MEMORY)(MEMORY+1)
# # test_script += go_add_n(MEMORY+1)(8+2)
# # test_script += int4_mul_x_y(MEMORY)(MEMORY+1)
# # test_script += clamp_x_move_y(REG2)(MEMORY+2)

# a_start, b_start, c_start = MEMORY, MEMORY+4, MEMORY+8
# # a alloc
# test_script += go_add_n(a_start)(8+1)
# test_script += go_add_n(a_start+1)(8+0)
# test_script += go_add_n(a_start+2)(8+1)
# test_script += go_add_n(a_start+3)(8+0)
# # b alloc
# test_script += go_add_n(b_start)(8)
# test_script += go_add_n(b_start+1)(9)
# test_script += go_add_n(b_start+2)(8)
# test_script += go_add_n(b_start+3)(9)
# test_script += matmul2x2(a_start)(a_start+2)(b_start)(b_start+2)(c_start)(c_start+2)
# test_script += "#"
