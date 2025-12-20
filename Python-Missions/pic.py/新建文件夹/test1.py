#!/usr/bin/env python3
import sys
import math

def main():
    rn = 55.3
    ra = 1000.0
    rb = 5000.0
    u0 = [0.0] * 10
    u = 3.0
    x = [0.0] * 10
    y = [0.0] * 10
    result = [0.0] * 10

    # Read up to 10 floats from stdin (tokens). If none provided, keep defaults (zeros).
    data = []
    if not sys.stdin.isatty():
        data = sys.stdin.read().split()
    else:
        try:
            line = input()
            data = line.split()
        except EOFError:
            data = []

    for i, token in enumerate(data[:10]):
        try:
            u0[i] = float(token)
        except ValueError:
            print(f"info: invalid float token at position {i}, using 0", file=sys.stderr)
            break

    for i in range(10):
        x[i] = rn * (u0[i] * (ra + rb) + u * rb)
        y[i] = (u - u0[i]) * (ra + rb) - u * rb
        if abs(y[i]) < 1e-9:
            print(f"warning: y[{i}] is zero (or nearly zero), skipping division", file=sys.stderr)
            result[i] = math.nan
        else:
            result[i] = x[i] / y[i]

    for i in range(10):
        print(f"x[{i}] = {x[i]:f}, y[{i}] = {y[i]:f}, result[{i}] = {result[i]:f}")

if __name__ == '__main__':
    main()
