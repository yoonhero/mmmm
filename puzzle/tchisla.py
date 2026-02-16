import json
import os
import subprocess
import math
import re

nat = {
    0: "+[]",
    1: "+!![]",
    2: "!![]+!![]",
    3: "!![]+!![]+!![]",
    4: "!![]+!![]+!![]+!![]",
    5: "!![]+!![]+!![]+!![]+!![]",
    6: "[2]*[3]",
    7: "[2]*[3]+i1",
    8: "i10-i1-i1", # 10 - 2
    9: "i10-i1", # 10 - 1
    10: "+i10",
    11: "+i11",
    22: "+i22",
    33: "+i33",
}

string_nat = {
    1: "!![]",
    10: "[[+!![]]+-+![]]", # 
    11: "[[+!![]]+[+!![]]]",
    22: "[[2]+[2]]",
    33: "[[3]+[3]]",
    100: "[[+!![]]+-+![]+-+![]]",
    1000: "[[+!![]]+-+![]+-+![]+-+![]]",
}

nums = list(map(str, range(10)))

def make_string_nat_with_concat(n):
    digits = [int(s) for s in str(n)]
    result = list(map(lambda d: f"[{nat[d]}]", digits))
    # result[0] = f"[{result[0]}]"
    return f"[{'+'.join(result)}]"

for i in range(10, 1000):
    if i not in string_nat:
        string_nat[i] = make_string_nat_with_concat(i)

def evaluate(expr):
    maxLen = len(expr)
    ptr = 0
    jsExpr = ""

    while ptr < maxLen:
        ch = expr[ptr]
        if ch == "i": pass
        elif ch in nums:
            prevPtr = ptr
            while ptr + 1 < maxLen and expr[ptr+1] in nums:
                ptr += 1
            number = int(expr[prevPtr:ptr+1])
            if prevPtr > 0 and expr[prevPtr-1] == "i" and number in string_nat:
                jsExpr += evaluate(string_nat[number])
            else:
                jsExpr += evaluate(nat[number])
        else:
            jsExpr += ch
        ptr += 1
    return jsExpr

def node_eval(expr: str):
    out = subprocess.check_output(["node", "-p", expr], text=True)
    return out.strip()

success = {}

def update(i, jsExpr):
    if len(jsExpr) <= 75:
        nat[i] = jsExpr
        success[i] = jsExpr
        return True
    
def get_failed():
    re = list(filter(lambda x: x not in success, range(1001)))
    return re

for i in range(1001):
    if i not in nat:
        jsExpr = evaluate(f"+i{string_nat[i]}")
    else:
        jsExpr = evaluate(nat[i])
    # result = node_eval(jsExpr)
    # if result != str(i) or len(jsExpr) > 75:
    update(i, jsExpr)

# for i in get_failed():
#     if i % 2 == 0:
#         jsExpr = evaluate(f"[2]*i{i//2}")
#         if update(i, jsExpr): continue

# for i in get_failed():
#     if 1000-i in nat:
#         jsExpr = evaluate(f"i1000-{1000-i}")
#         if update(i, jsExpr): continue
#     jsExpr = evaluate(f"i1000-i{1000-i}")
#     if update(i, jsExpr): continue

# print(dump["failed3"])
# print(len(dump["failed3"]))

# [167, 177, 257, 267, 275, 277, 287, 347, 356, 357, 365, 367, 374, 375, 376, 377, 379, 387, 397, 437, 447, 455, 457, 465, 467, 469, 473, 474, 475, 477, 479, 485, 487, 497, 527, 536, 537, 545, 546, 547, 548, 554, 555, 556, 557, 558, 559, 563, 565, 567, 569, 572, 573, 574, 575, 576, 577, 585, 587, 595, 596, 617, 627, 635, 637, 645, 647, 649, 653, 654, 655, 657, 659, 663, 665, 667, 671, 672, 673, 674, 675, 683, 685, 694, 695, 707, 716, 717, 725, 726, 727, 728, 734, 735, 736, 737, 738, 739, 743, 744, 745, 746, 747, 748, 749, 752, 753, 754, 755, 756, 757, 761, 763, 765, 771, 772, 773, 774, 775, 783, 785, 793, 794, 827, 837, 845, 847, 854, 855, 857, 863, 865, 872, 873, 874, 875, 937, 946, 955, 973]

# print("\n".join([f"{i}: {len(dump['success'][str(i)])}" for i in range(101)]))
# for i in get_failed():
#     fstDigit = round(i/100) # 가장 먼저 나오는 건 곱셈이나 덧셈보다 string으로 만드는 편이 현명함.
#     if fstDigit*100 - i > 0:
#         jsExpr = evaluate(f"i{fstDigit}00-i{fstDigit*100-i}")
#         if update(i, jsExpr): continue
#     else:
#         jsExpr = evaluate(f"i{fstDigit}00+i{i-fstDigit*100}")
#         if update(i, jsExpr): continue

# for i in get_failed():
#     if i % 2 == 0:
#         jsExpr = evaluate(f"[2]*i{i//2}")
#         if update(i, jsExpr): continue
#     if i % 2 == 1:
#         try:
#             a = success[i//2]
#             b = success[i//2+1]
#             if len(a) > len(b):
#                 jsExpr = evaluate(f"[2]*{b}-i1")
#             else:
#                 jsExpr = evaluate(f"[2]*{a}+i1")

#             if update(i, jsExpr): continue
#         except: pass

print(len(get_failed()))

import matplotlib.pyplot as plt
def draw():
    x = range(1001)
    y = map(lambda x: len(success[x]) if x in success else 0, x)
    plt.axhline(y=75, c="r")
    plt.axhline(y=35, c="b")
    plt.axvline(x=10, c="y")
    plt.plot(x, list(y))
    # plt.show()
    plt.savefig("data.jpg", dpi=400)
# [347, 356, 357, 374, 375, 473, 474, 475, 527, 536, 537, 545, 546, 547, 548, 554, 555, 556, 557, 558, 567, 572, 574, 576, 653, 654, 655, 671, 672, 673, 674, 675, 694, 707, 716, 717, 725, 726, 727, 728, 734, 735, 736, 737, 738, 739, 743, 744, 745, 746, 747, 748, 749, 752, 753, 754, 755, 756, 765, 771, 772, 773, 774, 775, 854, 855, 857, 872, 873, 874, 875, 937, 946, 955, 973]

# +-1/2/3/4/5/9
# 111/222/333
# explore = list(filter(lambda x: len(success[x])<=70, success.keys()))
# union = [(len(success[x]), x, success[x]) for x in success]
# pq = [(len(success[x]), x, success[x]) for x in success]

# import heapq
# heapq.heapify(pq)
# heapq.heappop(pq) # no need to explore 0

# patterns
# [n]+[m]
# [n]*[m]
# [n]-[m] -> +로 이루어진 m을 모조리 -로 바꾸기

def negate(expr):
    local = 0
    ptr = 0
    re = ""
    while ptr < len(expr):
        if expr[ptr] == "[":
            local += 1
        if expr[ptr] == "]":
            local -= 1
        if local == 0 and ptr != 0:
            match expr[ptr]:
                case "-": 
                    ptr += 1
                    re += "+"
                    continue
                case "+": 
                    ptr += 1
                    re += "-"
                    continue
        re += expr[ptr]
        ptr += 1
    return re

# print(negate("+[[!![]+!![]]+[+[]]+[+!![]]] "))

from collections import deque

# print(negate("!![]+!![]+!![]+!![]+!![]"))
stack = deque(success.keys())
stack.pop()
visited = {}

while stack and len(get_failed())!=0:
    # _, x = heapq.heappop(pq)
    print(get_failed())
    x = stack.pop()
    for y in range(1001):
        if y not in success: continue
        lh, rh = success[x], success[y]
        if x == 1:
            add = f"{rh}+!![]"
        elif y == 1:
            add = f"{lh}+!![]"
        else: add = f"{lh}-+-{rh}"

        sub = f"{lh}-+{negate(rh)}".replace('++', '+')
        minus = f"{rh}-+{negate(lh)}".replace('++', '+')
        mul = f"[{lh}]*[{rh}]"
        
        exprs = filter(lambda x: len(x[1]) <= 75, [(x+y,add), (x-y,sub), (y-x,minus), (x*y,mul)])
        for (v, expr) in exprs:
            if 0 < v < 1500:
                if v not in success or len(expr) < len(success[v]):
                    success[v] = expr
                    stack.append(v)

# # print(get_failed())
# print(len(success))
draw()
with open("success.json", "w") as f:
    sss = {i:success[i] for i in range(1001) if i in success}
    json.dump(sss, f)

# [734, 737, 739, 743, 745, 746, 749, 752, 754, 773, 774, 855, 857, 875]

with open("success.json", "r") as f:
    sss = json.load(f)

with open("success.txt", "w") as f:
    f.writelines([f"{sss[str(i)]}\n" for i in range(1001)])

# for (k, expr) in sss.items():
#     if node_eval(expr) != k:
#         print(k, expr)