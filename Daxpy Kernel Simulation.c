#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

#define N 10000  // Size of arrays
#define THREADS 4  // Number of threads

double a = 2.0;  // Scalar multiplier
double x[N], y[N];  // Arrays

typedef struct {
    int start, end;  // Range of work for this thread
} ThreadData;

void *daxpy_thread(void *arg) {
    ThreadData *data = (ThreadData *)arg;
    for (int i = data->start; i < data->end; i++) {
        y[i] = a * x[i] + y[i];
    }
    pthread_exit(NULL);
}

int main() {
    // Initialize x and y
    for (int i = 0; i < N; i++) {
        x[i] = 1.0;
        y[i] = 2.0;
    }

    pthread_t threads[THREADS];
    ThreadData thread_data[THREADS];

    int chunk = N / THREADS;  // Divide work among threads

    // Create threads
    for (int t = 0; t < THREADS; t++) {
        thread_data[t].start = t * chunk;
        thread_data[t].end = (t == THREADS - 1) ? N : (t + 1) * chunk;
        pthread_create(&threads[t], NULL, daxpy_thread, &thread_data[t]);
    }

    // Join threads
    for (int t = 0; t < THREADS; t++) {
        pthread_join(threads[t], NULL);
    }

    // Print a few results for verification
    printf("y[0] = %f\n", y[0]);
    printf("y[N-1] = %f\n", y[N-1]);

    return 0;
}
