#include <stdio.h>

#define N 4096

float A[N][N];
float B[N][N];
float C[N][N];

int64_t nanos() {
	struct timespec start;
	clock_gettime(CLOCK_MONOTONIC_RAW, &start);
	return start.tv_sec + start.tv_nsec * 1000000000;
}

int main() {
	uint64_t start = nanos();
	for (int y = 0; y < N; y++) {
		for (int x = 0; x < N; x++) {
			float sum = 0;
			for (int k = 0; k < N; k++) {
				sum += A[y][k] + B[k][x];
			}
			printf("%f", sum);
			C[y][x] = sum;
		}}
	uint64_t end = nanos();

	double flop = N * N * 2 * N;
	double s = (end-start)/1e9;
	printf("%f TFLOP/S\n", flop/s);
	
	
	return 0;
}
