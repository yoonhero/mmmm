#!/usr/bin/env python
# Always start at home.
home = 0
alloc_table = {
    'bump': 1,
    'input': 2,
    'apple': 3,
    'reg': 4,
    'if': 7, # [7:10] = 0 VALUE 0 1
    'counter': 11,
    'snake': 12 # heap memory
}
INPUT_AREA = alloc_table["input"]
IF_AREA = alloc_table["if"]
REG_AREA = alloc_table["reg"]
SNAKE_AREA = alloc_table["snake"]
COUNTER_AREA = alloc_table["counter"]

GO_FRONT = '>'
GO_BACK = '<'
INC = '+'
DEC = '-'
INPUT = ','
PRINT = '.'

####### BASICS #######
reset = '[-]'
loop = lambda work: f'[{work}]'
repeat = lambda work: lambda times: work*times

go_work_back = lambda x: lambda work: f'{repeat(GO_FRONT)(x)}{work}{repeat(GO_BACK)(x)}'
back_work_go = lambda x: lambda work: f'{repeat(GO_BACK)(x)}{work}{repeat(GO_FRONT)(x)}'

add_n = lambda n: repeat(INC)(n)
sub_n = lambda n: repeat(DEC)(n)
go_add_n = lambda x: lambda n: go_work_back(x)(add_n(n))
go_sub_n = lambda x: lambda n: go_work_back(x)(sub_n(n))

move = lambda d: f'[-{repeat(GO_FRONT if d>0 else GO_BACK)(abs(d))}+{repeat(GO_BACK if d>0 else GO_FRONT)(abs(d))}]'
move_a_to_b = lambda origin: lambda dest: go_work_back(origin)(move(dest-origin))
load_in_reg0 = lambda data_pos: move_a_to_b(data_pos)(REG_AREA)
load_in_reg1 = lambda data_pos: move_a_to_b(data_pos)(REG_AREA+1)
copy_reg0_to_reg1 = go_work_back(REG_AREA)('[->+>+<<]>>'+move(-2)+'<<')
reset_reg = go_work_back(REG_AREA)(f'{reset}>{reset}>{reset}<<')
load_data = lambda origin: lambda dest: load_in_reg0(origin)+copy_reg0_to_reg1+move_a_to_b(REG_AREA)(origin)+move_a_to_b(REG_AREA+1)(dest)

####### CONDITION #######
# reg_1 -> if_area_1
move_reg1_to_if1 = move_a_to_b(REG_AREA+1)(IF_AREA+1)
# use if_area_1
if_a_then_b = lambda a: lambda b: go_work_back(IF_AREA)(f'>{a}[<]>>[<{back_work_go(IF_AREA+2)(b)}]<{reset}<') # (0or1)0
move_reg1_if_a_then_b = lambda a: lambda b: move_reg1_to_if1 + if_a_then_b(a)(b)
# reg_0 == reg_1 + reg_2 not safe (it can be overrided)
if_equal = lambda b: go_work_back(REG_AREA)('[->-<]')+move_reg1_if_a_then_b('')(b)
if_nequal = lambda b: go_work_back(REG_AREA)(f'[->-<]>[{reset}+>]<[<]>-<')+move_reg1_if_a_then_b('')(b)

get_input = go_work_back(INPUT_AREA)(INPUT)
prepare_if_move = load_data(INPUT_AREA)(REG_AREA)
if_move = lambda n: lambda work: copy_reg0_to_reg1+move_reg1_if_a_then_b(sub_n(n))(work)
# w/a/s/d : 1/2/3/4
if_move_forward = if_move(1)(go_add_n(SNAKE_AREA)(8))
if_move_backward = if_move(3)(go_sub_n(SNAKE_AREA)(8))
if_move_left = if_move(2)(go_add_n(SNAKE_AREA)(1))
if_move_right = if_move(4)(go_sub_n(SNAKE_AREA)(1))

# caution: need to delete after drawing.
load_cursor = load_data(SNAKE_AREA)(-1)+'<[[<+>-]<-]'
back_home = '+[->+<[<<]>]>>-<'
draw_cursor = repeat(INC)(128)+PRINT 
delete_cursor = repeat(DEC)(128)

######## BUILD PROGRAM ##########
init_script = add_n(1) # set home 1
init_script += go_work_back(IF_AREA+3)(INC) # if trigger flag
init_script += go_add_n(SNAKE_AREA)(3)
# init_script += go_add_n(INPUT_AREA)(1)

work_script = ''
def add_line(work):
    global work_script
    work_script += work
    # work_script += go_work_back(COUNTER_AREA)(add_n(1))

### CHECK MOVE
# TODO: border...
add_line(get_input)
add_line(reset_reg)
add_line(prepare_if_move)
add_line(if_move_forward)
add_line(if_move_backward)
add_line(if_move_right)
add_line(if_move_left)

add_line(reset_reg)
add_line(load_cursor)
add_line(draw_cursor)
add_line(delete_cursor)
add_line(back_home)

main_script = loop(work_script)
script = init_script + main_script

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

bf_script = optimize(script)
print(f"Length: {len(bf_script)}\nResult: {bf_script}")
with open("test.bf", "w") as f:
    f.write(optimize(script))