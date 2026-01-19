#!/usr/bin/env python

draw_cursor = '++++++++++.'
delete_cursor = '----------.'

alloc_table = {
    'input': 1,
    'apple': 2,
    'reg': 3,
    'if': 6, # [6:9] = 0 VALUE 0 1
    'snake': 10
}
INPUT = alloc_table["input"]
IF = alloc_table["if"]
REG = alloc_table["reg"]
SNAKE = alloc_table["snake"]

FRONT = '>'
BACK = '<'
INC = '+'
DEC = '-'

####### BASICS #######
reset = '[-]'
loop = lambda work: f'[{work}]'
gotox = lambda dir: lambda x: dir*x
goworkback = lambda x: lambda work: f'{gotox(FRONT)(x)}{work}{gotox(BACK)(x)}'
backworkgo = lambda x: lambda work: f'{gotox(BACK)(x)}{work}{gotox(FRONT)(x)}'

change = lambda x: lambda how: lambda a: goworkback(x)(how*a)
move = lambda d: f'[-{gotox(FRONT if d>0 else BACK)(abs(d))}+{gotox(BACK if d>0 else FRONT)(abs(d))}]'
moveatob = lambda origin: lambda dest: goworkback(origin)(move(dest-origin))
copy = goworkback(REG)('[->+>+<<]>>'+move(-2))

####### CONDITION #######
ifathenb = lambda a: lambda b: moveatob(REG+1)(IF+1) + goworkback(IF)(f'>{a}[<]>>[<{backworkgo(IF+2)(b)}]<{reset}<') # (0or1)0
glide = ''

ifmovethenb = lambda move: lambda b: moveatob(INPUT)(REG+1)+ifathenb(move)(b)
# w/a/s/d : 1/2/3/4
ifmoveforward = ifmovethenb('-')(change(SNAKE)(INC)(8))
ifmovebackward = ifmovethenb('---')(change(SNAKE)(DEC)(8))
ifmoveright = ifmovethenb('----')(change(SNAKE)(DEC)(1))
ifmoveleft = ifmovethenb('--')(change(SNAKE)(INC)(1))
print(ifmoveforward)

init = '+'
init += goworkback(IF+3)('+') # if trigger flag

work = ''
main = loop(work)

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
print(optimize(ifmoveforward))