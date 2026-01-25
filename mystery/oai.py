#!/usr/bin/env python
import torch
import time

# def fwd(x: torch.Tensor):
#     return x.sort().values / x.median()
# -> x is 1d odd float vector
#
# This is oai interview(?) question i got from X

def benchmark(loop):
    iters = 100
    t0 = time.perf_counter()
    for _ in range(iters):
        loop()
    t1 = time.perf_counter()
    return (t1-t0) / iters 

L = 1001 # 4B * 1M = 4MB

### Phase 1: basic
x = torch.randn(L, requires_grad=True)
# more optimized call
sorted_values, sorted_idx = x.sort()
median = sorted_values[L//2] # warning at 0
y = sorted_values / median

dy = torch.ones_like(y)
# tmp = dy*sorted_values
# tmp[L//2] = 0
# dsorted = dy / median
# dsorted[L//2] = -tmp.sum()/(median**2) # -val/med**2
dot = torch.dot(dy, sorted_values)
dot_excl = dot - dy[L//2]*median
dsorted = dy / median
dsorted[L//2] = -dot_excl / (median**2)

# dx = torch.zeros_like(x)
# dx[sorted_idx] = dsorted
dx = torch.empty_like(x)
dx.scatter_(0, sorted_idx, dsorted) # and gather_

y.backward(gradient=dy) # y.sum().backward()
if x.grad != None:
    print(torch.allclose(x.grad, dx))

### Phase 2: Introduction to GPU-programming
# 
# GPU-ish guy
#   1. Argmax is costy than Random Sampling -> prefix sum is much more GPU-native
#   2. Moving a bit is much expensive.
#     ㄴ gpu hierarchy: Grid(software)-HBM > Block(SM)-L2 > Warp-L1(Shared) > Threads-Register
#	  ㄴ Deepseek using PTX: MoE(streaming core) / Register Pressure / private hardware call
#   3. Dynamic indexing is bad. Use vectorization instead. (list[dynamic] <<< list*mask)
#   4. GPU is actually fast - mul_add_: CPU-1ns / GPU-1μs & 2048x2048: CPU-28ms / GPU-209μs

# radix sort - malloc is $$$ -> in GPU, GOOD = static flow
# first thought rather choose quicksort -> divergence $$$ = data-dependent flow

# Example
#   ㄴ branching vs branchless
#     1. if (a > b) result = a*2;
#     2. result = (a>b)*(a*2)
#
#   ㄴ Bit Masking (abs)
#     1. if (x < 0) return -x; else return x;
#     2. 2-complement bit-mask