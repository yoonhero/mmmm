#!/usr/bin/env python
# Always start at home.
home = 0
alloc_table = {
    'bump': 1,
    'input': 2,
    'apple': 4,
    'reg': 6,
    'if': 10, # [if:if+3] = 0 VALUE 0 1
    'counter': 14,
    'snake_reg': 15,
    'snake_size': 16,
    'snake': 17 # heap memory
}
INPUT_AREA = alloc_table["input"]
APPLE_AREA = alloc_table["apple"]
IF_AREA = alloc_table["if"]
REG_AREA = alloc_table["reg"]
COUNTER_AREA = alloc_table["counter"]
SNAKE_REG_AREA = alloc_table["snake_reg"]
SNAKE_SIZE_AREA = alloc_table["snake_size"]
SNAKE_AREA = alloc_table["snake"]

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

####### CONDITION #######
# reg_1 -> if_area_1
move_reg1_to_if1 = move_a_to_b(REG_AREA+1)(IF_AREA+1)
# use if_area_1 / you don't need to clear in (b) execution.
if_a_then_b = lambda a: lambda b: go_work_back(IF_AREA)(f'>{a}[<]>>[<{back_work_go(IF_AREA+2)(b)}]<{reset}<') # 0=true / else=false
move_reg1_if_a_then_b = lambda a: lambda b: move_reg1_to_if1 + if_a_then_b(a)(b)
# reg_0 == reg_1 + reg_2 not safe (it can be overrided)
if_equal = lambda b: go_work_back(REG_AREA)('[->-<]')+move_reg1_if_a_then_b(NOTHING)(b)
if_nequal = lambda b: go_work_back(REG_AREA)(f'[->-<]>[{reset}+>]<[<]>-<')+move_reg1_if_a_then_b(NOTHING)(b)
if_x_nequal_y = lambda x: lambda y: lambda b: safe_load_xy_reg0_reg1(x)(y) + if_nequal(b)
if_x_nequal_m = lambda x: lambda m: lambda b: safe_load_data(x)(REG_AREA) + go_add_n(REG_AREA+1)(m) + if_nequal(b)
if_x_eq_y = lambda x: lambda y: lambda b: safe_load_xy_reg0_reg1(x)(y)+if_equal(b)
if_x_eq_a = lambda x: lambda a: lambda b: safe_load_data(x)(REG_AREA)+go_add_n(REG_AREA+1)(a)+if_equal(b)
EMPTY = lambda b: b
def nand_fixed(x, nums):
    if len(nums) == 0:
        return EMPTY
    current_condition = if_x_nequal_m(x)(nums[0])
    next_step = nand_fixed(x, nums[1:])
    return lambda b: current_condition(next_step(b))
if_reg0_geq_reg1 = lambda b: go_work_back(REG_AREA)('>[<<]>[->-[<<]>]>[>>]<<<')+move_reg1_if_a_then_b('')(b)
if_x_geq_y = lambda x: lambda y: lambda b: safe_load_xy_reg0_reg1(x)(y)+if_reg0_geq_reg1(b)
if_x_geq_a = lambda x: lambda a: lambda b: safe_load_data(x)(REG_AREA)+go_add_n(REG_AREA+1)(a)+if_reg0_geq_reg1(b)
if_x_gq_y = lambda x: lambda y: lambda b: if_x_nequal_y(x)(y)(if_x_geq_y(x)(y)(b))
if_x_gq_a = lambda x: lambda a: lambda b: if_x_nequal_m(x)(a)(if_x_geq_a(x)(a)(b))

get_input = go_work_back(INPUT_AREA+1)(INPUT)+safe_load_data(INPUT_AREA+1)(REG_AREA)+if_nequal(safe_move_a_to_b(INPUT_AREA+1)(INPUT_AREA)) # if input is non-zero, accept it.
# get_input = go_work_back(INPUT_AREA)(INPUT)
prepare_if_move = safe_load_data(SNAKE_AREA)(SNAKE_REG_AREA)+safe_load_data(INPUT_AREA)(REG_AREA)
if_move = lambda n: lambda work: copy_reg0_to_reg1+move_reg1_if_a_then_b(sub_n(n))(work)

if_ntouch_left = lambda b: nand_fixed(SNAKE_REG_AREA, list(range(7, 64, 8)))(b)
if_ntouch_right = lambda b: nand_fixed(SNAKE_REG_AREA, list(range(0, 64, 8)))(b)
if_ntouch_top = lambda b: nand_fixed(SNAKE_REG_AREA, list(range(56, 64, 1)))(b)
if_ntouch_bottom = lambda b: nand_fixed(SNAKE_REG_AREA, list(range(0, 8, 1)))(b)

# w/a/s/d : 1/2/3/4
if_move_forward = if_move(1)(if_ntouch_top(go_add_n(SNAKE_REG_AREA)(64))+go_sub_n(SNAKE_REG_AREA)(56))
if_move_backward = if_move(3)(if_ntouch_bottom(go_sub_n(SNAKE_REG_AREA)(64))+go_add_n(SNAKE_REG_AREA)(56))
if_move_left = if_move(2)(if_ntouch_left(go_add_n(SNAKE_REG_AREA)(8))+go_sub_n(SNAKE_REG_AREA)(7))
if_move_right = if_move(4)(if_ntouch_right(go_sub_n(SNAKE_REG_AREA)(8))+go_add_n(SNAKE_REG_AREA)(7))

# load_cursor = safe_load_data(SNAKE_AREA)(-1)+'<[[<+>-]<-]'
# back_home = '+[->+<[<<]>]>>-<'
draw_pixel = lambda pixel: repeat(INC)(pixel)
reset_screen = repeat(GO_BACK)(64)+repeat(reset+GO_FRONT)(64)
glider = loop(GO_BACK) # move until meet 0
# cursor_routine = DEC+back_work_go(REG_AREA)(f'[<]<[[>]<{go_work_back(REG_AREA)(DEC)}[<]<+>]>[<]+[>]<')
cursor_routine = lambda y: DEC+back_work_go(y)(f'[<]+[>]<')
load_cursor = lambda x: lambda y: lambda pixel: lambda work='': safe_load_data(x)(y)+work+go_work_back(y)(loop(cursor_routine(y)))+glider+draw_pixel(pixel)+'>[->]<+' 
load_apple = load_cursor(APPLE_AREA)(REG_AREA)(191)()

if_nth_gq_y_sub1 = lambda n: lambda y: if_x_gq_y(SNAKE_AREA+n)(y)(go_sub_n(SNAKE_REG_AREA)(1))
if_nth_gq_mth_sub1 = lambda n: lambda m: if_nth_gq_y_sub1(n)(SNAKE_AREA+m)
load_0th_snake = load_cursor(SNAKE_AREA)(SNAKE_REG_AREA)(63)(if_nth_gq_y_sub1(0)(APPLE_AREA))
load_nth_snake = lambda n: lambda cond: if_x_gq_a(SNAKE_SIZE_AREA)(n)(load_cursor(SNAKE_AREA+n)(SNAKE_REG_AREA)(63)(cond))
load_1th_snake = load_nth_snake(1)(if_nth_gq_y_sub1(1)(APPLE_AREA)+if_nth_gq_mth_sub1(1)(0))
load_2th_snake = load_nth_snake(2)(if_nth_gq_y_sub1(2)(APPLE_AREA)+if_nth_gq_mth_sub1(2)(0)+if_nth_gq_mth_sub1(2)(1))
load_3th_snake = load_nth_snake(3)(if_nth_gq_y_sub1(3)(APPLE_AREA)+if_nth_gq_mth_sub1(3)(0)+if_nth_gq_mth_sub1(3)(1)+if_nth_gq_mth_sub1(3)(2))
load_4th_snake = load_nth_snake(4)(if_nth_gq_y_sub1(4)(APPLE_AREA)+if_nth_gq_mth_sub1(4)(0)+if_nth_gq_mth_sub1(4)(1)+if_nth_gq_mth_sub1(4)(2)+if_nth_gq_mth_sub1(4)(3))
load_5th_snake = load_nth_snake(5)(if_nth_gq_y_sub1(5)(APPLE_AREA)+if_nth_gq_mth_sub1(5)(0)+if_nth_gq_mth_sub1(5)(1)+if_nth_gq_mth_sub1(5)(2)+if_nth_gq_mth_sub1(5)(3)+if_nth_gq_mth_sub1(5)(4))
load_6th_snake = load_nth_snake(6)(if_nth_gq_y_sub1(6)(APPLE_AREA)+if_nth_gq_mth_sub1(6)(0)+if_nth_gq_mth_sub1(6)(1)+if_nth_gq_mth_sub1(6)(2)+if_nth_gq_mth_sub1(6)(3)+if_nth_gq_mth_sub1(6)(4)+if_nth_gq_mth_sub1(6)(5))
load_7th_snake = load_nth_snake(7)(if_nth_gq_y_sub1(7)(APPLE_AREA)+if_nth_gq_mth_sub1(7)(0)+if_nth_gq_mth_sub1(7)(1)+if_nth_gq_mth_sub1(7)(2)+if_nth_gq_mth_sub1(7)(3)+if_nth_gq_mth_sub1(7)(4)+if_nth_gq_mth_sub1(7)(5)+if_nth_gq_mth_sub1(7)(6))

mod64 = lambda x: if_x_geq_a(x)(64)(go_sub_n(x)(64)+if_x_geq_a(x)(64)(go_sub_n(x)(64)+if_x_geq_a(x)(64)(go_sub_n(x)(64)))) # third time enough
shift_and_back = shift(1)+'<'
body_update = go_work_back(SNAKE_AREA+4)(shift_and_back*5+repeat(GO_FRONT)(5))+safe_move_a_to_b(SNAKE_REG_AREA)(SNAKE_AREA)
reset_nth_body = lambda n: if_x_eq_a(SNAKE_SIZE_AREA)(n)(go_work_back(SNAKE_AREA+n)(reset))
reset_apple = move_a_to_b(COUNTER_AREA)(APPLE_AREA) + mod64(APPLE_AREA)
if_head_touch_apple = if_x_eq_y(SNAKE_AREA)(APPLE_AREA)(go_add_n(SNAKE_SIZE_AREA)(1)+reset_apple) \
    +reset_nth_body(1)+reset_nth_body(2)+reset_nth_body(3)+reset_nth_body(4)+reset_nth_body(5)

end_game = '[]'
check_head_nth_collision = lambda n: if_x_geq_a(SNAKE_SIZE_AREA)(n)(if_x_eq_y(SNAKE_AREA)(SNAKE_AREA+n)(end_game))
check_head_collision = "".join(map(check_head_nth_collision, range(1,8)))

######## BUILD PROGRAM ##########
init_script = add_n(1) # set home 1
init_script += go_work_back(IF_AREA+3)(INC) # if trigger flag
init_script += go_add_n(SNAKE_SIZE_AREA)(1)
init_script += go_add_n(SNAKE_AREA)(4)
init_script += go_add_n(INPUT_AREA)(1)
init_script += go_add_n(APPLE_AREA)(11)

work_script = ''
def add_line(work):
    global work_script
    work_script += work

add_line(go_add_n(COUNTER_AREA)(11))
### CHECK MOVE
add_line(get_input)
add_line(prepare_if_move)
add_line(if_move_forward)
add_line(if_move_backward)
add_line(if_move_right)
add_line(if_move_left)
### SNAKE LOGIC
add_line(body_update)
add_line(if_head_touch_apple)
add_line(check_head_collision)

add_line(load_apple)
add_line(load_0th_snake)
add_line(load_1th_snake)
add_line(load_2th_snake)
add_line(load_3th_snake)
add_line(load_4th_snake)
add_line(load_5th_snake)
add_line(load_6th_snake)
add_line(load_7th_snake)
add_line(PRINT)
add_line(reset_screen)

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

bf_script = script
bf_script = optimize(script)
print(f"Length: {len(bf_script)}\nResult: {bf_script}")
with open("test.bf", "w") as f:
    f.write(bf_script)