#include <stdio.h>
#include <stdint.h>
#include <x86intrin.h>

#define REPS 100000

char* probe;	

static void flush(void *p) {
    asm volatile("mfence\nclflush 0(%0)\n" : : "c"(p) : "rax");
    //_mm_clflush(&p);
}

static void load(void *p) {
    asm volatile("mfence\nmovq (%0), %%rax\n" : : "c"(p) : "rax");
}
  
static int64_t reload(int flushed) {
    char *ptr = probe;
    if (flushed) {
        flush(ptr);
    } else {
        load(ptr);
    }

    uint64_t x = __rdtsc();
    load(ptr);
    return __rdtsc()-x;
}

static int64_t threshold() {
    long int time_flushed = 0;
    long int time_unflushed = 0;

    for (int i = 0; i < REPS; i++)
    {
        time_flushed += reload(1);
        time_unflushed += reload(0);
    }

    printf("on average it took this long to call unflushed: %ld\n", time_unflushed/REPS);
    printf("it took this long to call flushed: %ld\n", time_flushed/REPS);
    printf("average diff: %ld\n", (time_flushed-time_unflushed)/REPS);

    return (time_flushed+time_unflushed)/(2*REPS);

}

void main()
{   
    probe = malloc(20);
    int64_t thres = threshold();
    printf("computed threshold: %ld\n", thres);
}

