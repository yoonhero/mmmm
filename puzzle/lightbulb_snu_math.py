import sys
sys.setrecursionlimit(1000)

n = 20
side = 1 << (n // 2)
space = 1 << n

def phi(i):
    team = inttoteam(i)
    re = [0] * n
    for teammate in team:
        for i in range(teammate, n, teammate+1):
            re[i] = 1-re[i] # xor
    inds = []
    for i, e in enumerate(re):
        if e == 1: inds.append(i)
    return teamtoint(inds)

visited = [0]*space
cycles = []

def teamtoint(team):
    te = [0]*n
    for teammate in team: te[teammate] = 1
    te.reverse()
    return int("".join(map(str, te)), 2)

def inttoteam(i):
    team = []
    for i, e in enumerate(bin(i)[2:].rjust(n, "0")[::-1]):
        if e == "1": team.append(i)
    return team

cycle = []
def find_cycle(i, start=None):
    cycle.append(i)
    visited[i] = 1
    if start is None: start = i
    if phi(i) == start:
        return cycle
    return find_cycle(phi(i), start)

for i in range(space):
    if visited[i] != 0:
        continue
    visited[i] = 1
    find_cycle(i)
    cycles.append(cycle)
    cycle = []


# with open("cycle20.txt", "w") as f:
    # f.write("".join(map(lambda cycle: f"({', '.join(map(str, cycle))})", cycles)))

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def generate_colors(k, seed=42):
    rng = np.random.default_rng(seed)
    colors = (rng.random((k, 3))*256).astype(np.uint8)
    return colors

num_cycles = len(cycles)
colors = generate_colors(num_cycles)

img = np.zeros((side, side, 3), dtype=np.uint8)

for color, cycle in zip(colors, cycles):
    for node in cycle:
        y, x = divmod(node, side)
        img[y, x, :] = color

Image.fromarray(img).save("cycle20.png")