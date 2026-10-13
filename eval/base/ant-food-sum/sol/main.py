import sys


def main():
    data = sys.stdin.buffer.read().split()
    n, q = int(data[0]), int(data[1])
    pre = [0] * (n + 1)
    for i in range(n):
        pre[i + 1] = pre[i] + int(data[2 + i])
    out = []
    pos = 2 + n
    for _ in range(q):
        l, r = int(data[pos]), int(data[pos + 1])
        pos += 2
        out.append(pre[r] - pre[l - 1])
    sys.stdout.write("\n".join(map(str, out)) + "\n")


main()
