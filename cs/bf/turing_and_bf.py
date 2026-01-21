#!/usr/bin/env python

# MEMORY ARRANGEMENT
# 1 -1  0  0  0  0  -1 -1  0 -1 1 
# <re>  <  reg   >  <    if     >
# (-1 indicates un-used lot, non-zero is pre-defined value)
memory_arrangement = {
    'home': 0,
    'reg': 2,
    'if': 6
}

# Always start at home.
HOME = memory_arrangement["home"]
IF_AREA = memory_arrangement["if"]+1
REG_AREA = memory_arrangement["reg"]

GO_FRONT = '>'
GO_BACK = '<'
INC = '+'
DEC = '-'
INPUT = ','
PRINT = '.'
NOTHING = ''

####### BASICS #######
reset = '[-]'
loop = lambda work: f'[{work}]'
repeat = lambda work: lambda times: work*times

go_work_back = lambda x: lambda work: f'{repeat(GO_FRONT)(x)}{work}{repeat(GO_BACK)(x)}'
back_work_go = lambda x: lambda work: f'{repeat(GO_BACK)(x)}{work}{repeat(GO_FRONT)(x)}'
reset_x = lambda x: go_work_back(x)(reset)

add_n = lambda n: repeat(INC)(n)
sub_n = lambda n: repeat(DEC)(n)
go_add_n = lambda x: lambda n: go_work_back(x)(add_n(n))
go_sub_n = lambda x: lambda n: go_work_back(x)(sub_n(n))

###### REG ACTIONS #######
shift = lambda d: f'[-{repeat(GO_FRONT if d>0 else GO_BACK)(abs(d))}+{repeat(GO_BACK if d>0 else GO_FRONT)(abs(d))}]' if d != 0 else ''
move_a_to_b = lambda origin: lambda dest: go_work_back(origin)(shift(dest-origin))
safe_move_a_to_b = lambda origin: lambda dest: (reset_x(dest) if origin != dest else '') +move_a_to_b(origin)(dest)
load_in_reg0 = lambda data_pos: move_a_to_b(data_pos)(REG_AREA)
load_in_reg1 = lambda data_pos: move_a_to_b(data_pos)(REG_AREA+1)
copy_reg0_to_reg1 = go_work_back(REG_AREA)('[->+>+<<]>>'+shift(-2)+'<<')
reset_reg = go_work_back(REG_AREA)(f'{reset}>{reset}>{reset}>{reset}<<<')
load_data = lambda origin: lambda dest: load_in_reg0(origin)+copy_reg0_to_reg1+move_a_to_b(REG_AREA)(origin)+safe_move_a_to_b(REG_AREA+1)(dest) # reg should reset before exec it
safe_load_data = lambda origin: lambda dest: reset_reg+load_data(origin)(dest)
safe_load_xy_reg0_reg1 = lambda x: lambda y: safe_load_data(x)(REG_AREA)+safe_move_a_to_b(REG_AREA)(REG_AREA+3)+load_data(y)(REG_AREA+1)+move_a_to_b(REG_AREA+3)(REG_AREA)

###### LOGICS #######
# reg_1 -> if_area_1
move_reg1_to_if1 = move_a_to_b(REG_AREA+1)(IF_AREA+1)
# use if_area_1 / you don't need to clear in (b) execution.
if_a_then_b = lambda a: lambda b: go_work_back(IF_AREA)(f'>{a}[<]>>[<{back_work_go(IF_AREA+2)(b)}]<{reset}<') # 0=true / else=false
move_reg1_if_a_then_b = lambda a: lambda b: move_reg1_to_if1 + if_a_then_b(a)(b)
# reg_0 == reg_1 + reg_2 not safe (it can be overrided)
if_eq = lambda b: go_work_back(REG_AREA)('[->-<]')+move_reg1_if_a_then_b(NOTHING)(b)
if_neq = lambda b: go_work_back(REG_AREA)(f'[->-<]>[{reset}+>]<[<]>-<')+move_reg1_if_a_then_b(NOTHING)(b)
if_x_neq_y = lambda x: lambda y: lambda b: safe_load_xy_reg0_reg1(x)(y) + if_neq(b)
if_x_neq_m = lambda x: lambda m: lambda b: safe_load_data(x)(REG_AREA) + go_add_n(REG_AREA+1)(m) + if_neq(b)
if_x_eq_y = lambda x: lambda y: lambda b: safe_load_xy_reg0_reg1(x)(y)+if_eq(b)
if_x_eq_a = lambda x: lambda a: lambda b: safe_load_data(x)(REG_AREA)+go_add_n(REG_AREA+1)(a)+if_eq(b)
EMPTY = lambda b: b
def nand_fixed(x, nums):
    if len(nums) == 0:
        return EMPTY
    current_condition = if_x_neq_m(x)(nums[0])
    next_step = nand_fixed(x, nums[1:])
    return lambda b: current_condition(next_step(b))
if_reg0_geq_reg1 = lambda b: go_work_back(REG_AREA)('>[<<]>[->-[<<]>]>[>>]<<<')+move_reg1_if_a_then_b('')(b)
if_x_geq_y = lambda x: lambda y: lambda b: safe_load_xy_reg0_reg1(x)(y)+if_reg0_geq_reg1(b)
if_x_geq_a = lambda x: lambda a: lambda b: safe_load_data(x)(REG_AREA)+go_add_n(REG_AREA+1)(a)+if_reg0_geq_reg1(b)
if_x_gq_y = lambda x: lambda y: lambda b: if_x_neq_y(x)(y)(if_x_geq_y(x)(y)(b))
if_x_gq_a = lambda x: lambda a: lambda b: if_x_neq_m(x)(a)(if_x_geq_a(x)(a)(b))

mod64 = lambda x: if_x_geq_a(x)(64)(go_sub_n(x)(64)+if_x_geq_a(x)(64)(go_sub_n(x)(64)+if_x_geq_a(x)(64)(go_sub_n(x)(64)))) # third time enough
shift_and_back = shift(1)+'<'

def optimize(code):
    from collections import deque
    optimized = ''
    buf = deque()
    def flush():
        nonlocal optimized
        optimized += "".join(buf)
    for cur in code:
        if len(buf) != 0:
            prev = buf.pop()
            if (cur == GO_FRONT and prev == GO_BACK) or (cur == GO_BACK and prev == GO_FRONT) or (cur == INC and prev == DEC) or (cur == DEC and prev == INC):
                continue
            buf.append(prev)
            buf.append(cur)
        else:
            buf.append(cur)
    flush()
    return optimized

init_script = add_n(1) # set home 1
init_script += go_add_n(IF_AREA+3)(1) # if trigger flag
