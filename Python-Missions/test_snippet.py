#!/usr/bin/env python3
import sys
import math

def main():
    # Initialize arrays like the C snippet
    t = [0.0] * 10
    t1 = [0.0] * 10

    # Read up to 10 floats from stdin (whitespace separated).
    tokens = []
    try:
        if not sys.stdin.isatty():
            tokens = sys.stdin.read().split()
        else:
            # Interactive: read up to 10 values line by line until EOF or 10 read
            for _ in range(10):
                try:
                    line = input()
                except EOFError:
                    break
                if not line:
                    break
                tokens.extend(line.split())
    except Exception:
        pass

    for i, tok in enumerate(tokens[:10]):
        try:
            t[i] = float(tok)
        except ValueError:
            print(f"info: invalid float token at position {i}, using 0", file=sys.stderr)
            t[i] = 0.0

    # Compute t1 = 1 / t with division-by-zero handling, and print results
    for i in range(10):
        if abs(t[i]) < 1e-12:
            print(f"warning: t[{i}] is zero (or nearly zero), skipping division", file=sys.stderr)
            t1[i] = math.nan
        else:
            t1[i] = 1.0 / t[i]
        print(f"t1[{i}] = {t1[i]:f}")

if __name__ == '__main__':
    main()
