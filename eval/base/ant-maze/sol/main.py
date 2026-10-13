import sys


def main():
    data = sys.stdin.buffer.read().split()
    n, m = int(data[0]), int(data[1])
    w = m + 2  # 테두리를 벽으로 둘러 범위 검사를 없앤다
    wall = bytearray(b"#" * (w * (n + 2)))
    for r in range(n):
        wall[(r + 1) * w + 1:(r + 1) * w + 1 + m] = data[2 + r]
    start, goal = w + 1, n * w + m
    dist = [-1] * len(wall)
    dist[start] = 0
    frontier = [start]
    steps = 0
    while frontier and dist[goal] == -1:
        steps += 1
        nxt = []
        for cur in frontier:
            for nb in (cur - 1, cur + 1, cur - w, cur + w):
                if dist[nb] == -1 and wall[nb] == 46:  # '.'
                    dist[nb] = steps
                    nxt.append(nb)
        frontier = nxt
    print(dist[goal])


main()
