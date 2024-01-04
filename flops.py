#! /usr/bin/env python3
import numpy as np
import time

N = 8192

if __name__ == "__main__":
	a = np.random.randn(N, N).astype(np.float32)
	b = np.random.randn(N, N).astype(np.float32)

	# Output NbyN matrix and one cell accompanied (N+N) caclculations. 
	flop = N * N * 2 * N
	print(f"{flop/1e9} GFLOP")

	st = time.monotonic()
	C = a @ b
	et = time.monotonic()

	spent = et - st
	print(f"{flop/1e12/spent} TFLOP/S")


