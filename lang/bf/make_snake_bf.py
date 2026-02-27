#!/usr/bin/env python
from turing_and_bf import *

alloc_table = {
    'input': 11,
    'apple': 13,
    'counter': 14,
    'snake_reg': 15,
    'snake_size': 16,
    'snake': 17, # heap memory
    'memory': 64
}

INPUT_AREA = alloc_table["input"]
APPLE_AREA = alloc_table["apple"]
COUNTER_AREA = alloc_table["counter"]
SNAKE_REG_AREA = alloc_table["snake_reg"]
SNAKE_SIZE_AREA = alloc_table["snake_size"]
SNAKE_AREA = alloc_table["snake"]

BIP = '!'

get_input = go_work_back(INPUT_AREA+1)(INPUT)+safe_load_data(INPUT_AREA+1)(REG_AREA)+if_neq(safe_move_a_to_b(INPUT_AREA+1)(INPUT_AREA)) # if input is non-zero, accept it.
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

SCREEN_SIZE = 64
SNAKE_PIXEL = 63
APPLE_PIXEL = 191
draw_pixel = lambda pixel: repeat(INC)(pixel)
reset_screen = repeat(GO_BACK)(SCREEN_SIZE)+repeat(reset+GO_FRONT)(SCREEN_SIZE)
glider = loop(GO_BACK) # move until meet 0
cursor_routine = lambda y: DEC+back_work_go(y)(f'[<]+[>]<')
load_cursor = lambda x: lambda y: lambda pixel: lambda work='': safe_load_data(x)(y)+work+go_work_back(y)(loop(cursor_routine(y)))+glider+draw_pixel(pixel)+'>[->]<+' 
load_apple = load_cursor(APPLE_AREA)(REG_AREA)(APPLE_PIXEL)()
reset_apple = move_a_to_b(COUNTER_AREA)(APPLE_AREA) + mod64(APPLE_AREA)

MAX_SNAKE_LENGTH = 8
if_nth_gq_y_sub1 = lambda n: lambda y: if_x_gq_y(SNAKE_AREA+n)(y)(go_sub_n(SNAKE_REG_AREA)(1))
load_0th_snake = load_cursor(SNAKE_AREA)(SNAKE_REG_AREA)(SNAKE_PIXEL)(if_nth_gq_y_sub1(0)(APPLE_AREA))

if_nth_gq_mth_sub1 = lambda n: lambda m: if_nth_gq_y_sub1(n)(SNAKE_AREA+m)
load_nth_snake = lambda n: lambda cond: if_x_neq_y(SNAKE_AREA+n)(APPLE_AREA)(if_x_gq_a(SNAKE_SIZE_AREA)(n)(load_cursor(SNAKE_AREA+n)(SNAKE_REG_AREA)(SNAKE_PIXEL)(cond)))
nth_sub1_cond = lambda n: if_nth_gq_y_sub1(n)(APPLE_AREA)+"".join([if_x_neq_y(SNAKE_AREA+m)(APPLE_AREA)(if_nth_gq_mth_sub1(n)(m)) for m in range(n)])
load_nth_snake_with_cond = lambda n: load_nth_snake(n)(nth_sub1_cond(n))
load_upto_nth_snake = lambda n: "".join(map(load_nth_snake_with_cond, range(n+1)))
load_snake = load_upto_nth_snake(MAX_SNAKE_LENGTH-1)

body_update = go_work_back(SNAKE_AREA+MAX_SNAKE_LENGTH-1)(shift_and_back*MAX_SNAKE_LENGTH+repeat(GO_FRONT)(MAX_SNAKE_LENGTH))+safe_move_a_to_b(SNAKE_REG_AREA)(SNAKE_AREA)
reset_if_size_eq_n = lambda n: if_x_eq_a(SNAKE_SIZE_AREA)(n)(go_work_back(SNAKE_AREA+n+1)(reset))
if_head_touch_apple = if_x_neq_m(SNAKE_SIZE_AREA)(MAX_SNAKE_LENGTH)(if_x_eq_y(SNAKE_AREA)(APPLE_AREA)(go_add_n(SNAKE_SIZE_AREA)(1)+reset_apple+BIP)) \
    +"".join(map(reset_if_size_eq_n, range(1, MAX_SNAKE_LENGTH+1)))

end_game = '[]'
check_head_nth_collision = lambda n: if_x_geq_a(SNAKE_SIZE_AREA)(n)(if_x_eq_y(SNAKE_AREA)(SNAKE_AREA+n)(end_game))
check_head_collision = "".join(map(check_head_nth_collision, range(1, MAX_SNAKE_LENGTH)))

######## BUILD PROGRAM ##########
init_snake = init_script
init_snake += go_add_n(SNAKE_SIZE_AREA)(1)
init_snake += go_add_n(SNAKE_AREA)(4)
init_snake += go_add_n(INPUT_AREA)(1)
init_snake += go_add_n(APPLE_AREA)(11)

work_script = ''
def add_line(work):
    global work_script
    work_script += work

add_line(go_add_n(COUNTER_AREA)(11)) # randomnized apple position

### CHECK MOVE
if __name__ == "__main__":
    add_line(get_input)
add_line(prepare_if_move)
add_line(if_move_forward)
add_line(if_move_backward)
add_line(if_move_right)
add_line(if_move_left)

### SNAKE LOGIC (current head on SNK_REG_AREA)
add_line(body_update)
add_line(if_head_touch_apple)
add_line(check_head_collision)

### DISPLAY
add_line(load_apple)
add_line(load_snake)
add_line(PRINT)
add_line(reset_screen)

main_script = loop(work_script)
script = init_snake + main_script

bf_script = script
bf_script = optimize(script)
if __name__ == "__main__":
    print(f"Length: {len(bf_script)}\nResult: {bf_script}")
    with open("snake.bf", "w") as f:
        f.write(bf_script)