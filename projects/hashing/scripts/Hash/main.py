#!/usr/bin/env python3
import sys
import hashlib


def hash_file(filepath: str, algorithm: str = "sha256") -> str:
    h = hashlib.new(algorithm)
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
    except FileNotFoundError:
        print(f"Error: file '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: permission denied reading '{filepath}'.", file=sys.stderr)
        sys.exit(1)
    return h.hexdigest()


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <file> [algorithm]", file=sys.stderr)
        print("  algorithm defaults to sha256", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    algorithm = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] in hashlib.algorithms_available else "sha256"

    try:
        hashlib.new(algorithm)
    except ValueError:
        print(f"Error: unsupported algorithm '{algorithm}'.", file=sys.stderr)
        sys.exit(1)

    print(hash_file(filepath, algorithm))


if __name__ == "__main__":
    main()
