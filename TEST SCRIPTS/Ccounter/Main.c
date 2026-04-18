#include <stdio.h>
#include <stdlib.h>
#include <unistd.h> // for sleep()

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: ./main <number>\n");
        return 1;
    }

    int count = atoi(argv[1]);

    if (count < 0) {
        printf("Please provide a non-negative number.\n");
        return 0;
    }

    while (count >= 0) {
        printf("%d\n", count);
        if (count > 0) {
            sleep(1); // wait 1 second
        }
        count--;
    }

    printf("Countdown complete!\n");

    return 0;
}