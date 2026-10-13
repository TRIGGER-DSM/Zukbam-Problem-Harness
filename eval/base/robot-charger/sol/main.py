import sys


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    it = iter(map(int, data[1:1 + 2 * n]))
    pairs = sorted((e, s) for s, e in zip(it, it))
    cnt = last = 0
    for e, s in pairs:
        if s >= last:
            cnt += 1
            last = e
    print(cnt)


main()
