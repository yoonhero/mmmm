#!/usr/bin/env python
# Always start at home.
home = 0
alloc_table = {
    'input': 1,
    'apple': 2,
    'reg': 3,
    'if': 6, # [6:9] = 0 VALUE 0 1
    'snake': 10 # heap memory
}
INPUT_AREA = alloc_table["input"]
IF_AREA = alloc_table["if"]
REG_AREA = alloc_table["reg"]
SNAKE_AREA = alloc_table["snake"]

FRONT = '>'
BACK = '<'
INC = '+'
DEC = '-'
INPUT = ','
PRINT = '.'

####### BASICS #######
reset = '[-]'
loop = lambda work: f'[{work}]'
go_dir_by_x = lambda dir: lambda x: dir*x
go_work_back = lambda x: lambda work: f'{go_dir_by_x(FRONT)(x)}{work}{go_dir_by_x(BACK)(x)}'
back_work_go = lambda x: lambda work: f'{go_dir_by_x(BACK)(x)}{work}{go_dir_by_x(FRONT)(x)}'

change = lambda x: lambda how: lambda a: go_work_back(x)(how*a)
move = lambda d: f'[-{go_dir_by_x(FRONT if d>0 else BACK)(abs(d))}+{go_dir_by_x(BACK if d>0 else FRONT)(abs(d))}]'
move_a_to_b = lambda origin: lambda dest: go_work_back(origin)(move(dest-origin))
load_in_reg0 = lambda data_pos: move_a_to_b(data_pos)(REG_AREA)
load_in_reg1 = lambda data_pos: move_a_to_b(data_pos)(REG_AREA+1)
copy_reg0_to_reg1 = go_work_back(REG_AREA)('[->+>+<<]>>'+move(-2))

####### CONDITION #######
# reg_1 -> if_area_1
move_reg1_to_if1 = move_a_to_b(REG_AREA+1)(IF_AREA+1)
# use if_area_1
if_a_then_b = lambda a: lambda b: go_work_back(IF_AREA)(f'>{a}[<]>>[<{back_work_go(IF_AREA+2)(b)}]<{reset}<') # (0or1)0
move_if_a_then_b = lambda a: lambda b: move_reg1_to_if1 + if_a_then_b(a)(b)
# reg_0 == reg_1 + reg_2 not safe (it can be overrided)
if_equal = lambda b: go_work_back(REG_AREA)('[->-<]')+move_if_a_then_b('')(b)
if_nequal = lambda b: go_work_back(REG_AREA)(f'[->-<]>[{reset}+>]<[<]>-<')+move_if_a_then_b('')(b)

prepare_if_move = move_a_to_b(INPUT_AREA)(REG_AREA+1)
# w/a/s/d : 1/2/3/4
if_move_forward = if_a_then_b('-')(change(SNAKE_AREA)(INC)(8))
if_move_backward = if_a_then_b('---')(change(SNAKE_AREA)(DEC)(8))
if_move_right = if_a_then_b('----')(change(SNAKE_AREA)(DEC)(1))
if_move_left = if_a_then_b('--')(change(SNAKE_AREA)(INC)(1))

# caution: need to delete after drawing.
draw_cursor = change(INC)(10)+PRINT 
delete_cursor = change(DEC)(10)+PRINT
move_cursor = move_a_to_b(SNAKE_AREA)

######## BUILD PROGRAM ##########
init_script = '+'
init_script += go_work_back(IF_AREA+3)('+') # if trigger flag

work_script = ''
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
            if (cur == FRONT and prev == BACK) or (cur == BACK and prev == FRONT) or (cur == INC and prev == DEC) or (cur == DEC and prev == INC):
                continue
            buf.append(prev)
            buf.append(cur)
        else:
            buf.append(cur)
    flush()
    return optimized

print(f"Result: \n\n{optimize(script)}")
with open("test.bf", "r") as f:
    f.write(optimize(script))