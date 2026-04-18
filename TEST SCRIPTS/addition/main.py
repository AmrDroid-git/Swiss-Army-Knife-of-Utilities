import sys

# Check if enough arguments are provided
if len(sys.argv) != 3:
    print("Usage: python script.py <a> <b>")
    sys.exit(1)

# Convert arguments to numbers
a = float(sys.argv[1])
b = float(sys.argv[2])

# Compute sum
result = a + b

# Print result
print("Sum:", result)