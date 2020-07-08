#include <stdlib.h>
#include <stdio.h>

char* data;	


int main() {
    data = malloc(20);
    for (int i = 0; i < 20; i++)
    {
        int r =  rand() % 95 + 32; // Get ASCII character in [32,127], i.e. in the range of printable characters
        data[i] = r; 
    }

    printf("Created random printable character array: %s\n", data);
    
} 
