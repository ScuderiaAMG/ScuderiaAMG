import sys
import math

def main():
    # 这里的rn ra rb是对应卧式电桥的，如果要用这个计算立式电桥的结果，需要修改对应位置电阻值
    # 输出result[i]是rx计算结果，ln(result[i])是取自然对数后的结果，在卧式电桥中用不到对数，自己注释一下就好
    rn = 100.0
    ra = 100.0
    rb = 3697.1
    u0 = [0.0] * 10
    u = 3.0
    x = [0.0] * 10
    y = [0.0] * 10
    result = [0.0] * 10

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
            print(f"invalid float {i}, use 0 instead", file=sys.stderr)
            break

    for i in range(10):
        x[i] = rn * (u0[i] * (ra + rb) + u * rb)
        y[i] = (u - u0[i]) * (ra + rb) - u * rb
        if abs(y[i]) < 1e-9:
            print(f"y[{i}] = 0", file=sys.stderr)
            result[i] = math.nan
        else:
            result[i] = x[i] / y[i]

    for i in range(10):
        ln_value = math.nan
        if math.isfinite(result[i]) and result[i] > 0.0:
            ln_value = math.log(result[i])
        else:
            print(f"result[{i}] error！", file=sys.stderr)
        print(f"x[{i}] = {x[i]:f}, y[{i}] = {y[i]:f}, result[{i}] = {result[i]:f}, ln(result)[{i}] = {ln_value:.6f}")

if __name__ == '__main__':
    main()
