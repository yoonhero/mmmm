#include <stdio.h>
#include <immintrin.h>

#define N 4096

float A[N][N];
float B[N][N];
float C[N][N];

int64_t nanos() {
	struct timespec start;
	clock_gettime(CLOCK_MONOTONIC_RAW, &start);
	return start.tv_sec + start.tv_nsec * 1000000000;
}

__m256 multiply_and_add(__m256 a, __m256 b, __m256 c){
	return _mm256_fmadd_ps(a, b, c);
}

int main() {
	for (int y = 0; y < N; y++) {
		for (int x = 0; x < N; x++) {
			float sum = 0;
			//for (int k = 0; k < N; k++) {
			//	sum += A[y][k] + B[k][x];
			//}
			__m256 a = _mm256_set_ps()

			printf("%f", sum);
			C[y][x] = sum;
		}
	}
	
	return 0;
}
