#!/usr/bin/env python3
import sys
import time

def countdown(start_number):
    """Count down from start_number to 0, printing each second."""
    try:
        # Convert to integer
        count = int(start_number)

        if count < 0:
            print("Please provide a non-negative number.")
            return

        # Count down
        while count >= 0:
            print(count)
            if count > 0:
                time.sleep(1)
            count -= 1

        print("Countdown complete!")

    except ValueError:
        print(f"Error: '{start_number}' is not a valid number.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python countdown.py <number>")
        sys.exit(1)

    countdown(sys.argv[1])