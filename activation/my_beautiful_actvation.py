# import torch
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import plotly.graph_objects as go

division = [
    (1, 1, -1),
    (1, -2, 1),
    (3, 1, 1),
] # 6

division = [
    (1, 0, 0.2), 
    (1, 0, -0.2), 
    (0, 1, 0),    
    (1, -1, 0.1), 
]

division = [
    (1, 1, 0),
    (1, -1, 0),
    (2, 1, 0),
    (-1, 3, 0),
] # 8

division = [
    (0.5, -1.2, 0.1),
    (-1.3, 0.8, -0.4),
    (2.1, 1.5, 0.3),
    (-0.9, -1.7, 0.5),
    (1.4, 0.6, -0.2),
    (-0.3, -0.4, 0.1)
] # 15

hi = 1
lo = -1

def relu(arr):
    mask = (arr > 0) * 1.0
    return arr * mask

# f(x, y) = Ax + By + c.
# check the 0-level set.
def levelset(a, b, c, level=0):
    n = 10
    x = np.linspace(lo, hi, n)
    if b != 0:
        return np.stack([x, -(a/b)*x-c/b+level], axis=1)
    else:
        return np.stack([np.array([-c/a]*n), x], axis=1)

def is_line_bounded(line):
    z = levelset(*line)
    return np.any((np.abs(z) < hi).sum(axis=1)==2)

def is_bounded(pt):
    return np.all((np.abs(pt) < hi))

def get_intersection(line1, line2):
    a1, b1, c1 = line1
    a2, b2, c2 = line2
    det = (a1*b2-a2*b1)
    if det == 0:
        return None
    return (1/det) * np.array([[b2, -b1], [-a2, a1]]) @ np.array([-c1, -c2])

def how_many_closed_sub_space(division):
    closed = 1
    lines = []
    for line in division:
        if not is_line_bounded(line): # if not bounded on [-hi, hi], we don't need to consider its line.
            continue
        intersects = []
        for another in lines:
            intersect = get_intersection(another, line)
            if intersect is None or not is_bounded(intersect): continue
            else: intersects.append(tuple(intersect.tolist()))
        intersects = set(intersects)
        closed = closed + len(intersects) + 1
        lines.append(line)
    return closed

def linear(v, division):
    linear = np.array([[line[0], line[1]] for line in division]).T
    c = np.array([line[2] for line in division])
    return v @ linear + c

def get_vector():
    xx = np.linspace(lo, hi, 100)
    x, y = np.meshgrid(xx, xx)
    v = np.stack([x, y], axis=2)
    return v

def coloring(division):
    v = get_vector()
    act_count = ((linear(v, division))>0).sum(axis=2).astype(float)
    act_count /= len(division)
    return act_count

def render_relu(division):
    v = get_vector()
    return relu(linear(v, division)).sum(axis=2)

if __name__ == "__main__":
    print(how_many_closed_sub_space(division))
