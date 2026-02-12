#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt

# Elementary cellular automata
# 111 / 110 / 101 / 100 / 011 / 010 / 001 / 000

rule = 0b00011110 # 00011110
#neighbors = [f"{7-i:03b}" for i in range(8)]
ruleMap = {7-i: int(f"{rule:08b}"[i]) for i in range(8)}
state = [1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1]

on = "█"
off = "_"
indent = 0

def step(state):
    if len(state) <= 2:
        return []
    newState = [0]*(len(state)-2)
    for i, (a, b, c) in enumerate(zip(state, state[1:], state[2:])):
        k = 4*a+2*b+c
        newState[i] = ruleMap[k]
    return newState

def clear():
    print("\033[2J") # clear page
    print("\033[H") # set home position

def render(state):
    print(" "*indent, end="")
    for s in state:
        print(on if s else off, end="")
    print("\n")

while True:
    render(state)
    state = step(state)
    indent += 1
    if len(state) == 0:
          break
