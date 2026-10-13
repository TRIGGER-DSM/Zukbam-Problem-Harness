"""사용: gen.py <n> <m> <모드> <seed>
모드: random p      벽 확률 p(%)로 랜덤 (예: random30)
      open          벽 없음
      snake         뱀 모양 외길 (경로가 가장 긴 경우)
      blocked       출발점 주변이 막혀 도착 불가
      detour        DFS가 먼 길을 먼저 가게 되는 격자 (오른쪽으로 길게 돌아가는 길 + 아래로 가는 짧은 길)
      corner        대각선 방향으로만 이어진 칸 (대각선 이동을 허용하면 도착함)
"""
import random
import sys

n, m, mode, seed = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4]
rnd = random.Random(f"{n} {m} {mode} {seed}")
g = [["."] * m for _ in range(n)]
if mode.startswith("random"):
    p = int(mode[6:])
    g = [["#" if rnd.randrange(100) < p else "." for _ in range(m)] for _ in range(n)]
elif mode == "snake":
    for r in range(1, n, 2):
        for c in range(m):
            g[r][c] = "#"
        g[r][m - 1 if r % 4 == 1 else 0] = "."
elif mode == "blocked":
    g = [["." if rnd.randrange(100) < 70 else "#" for _ in range(m)] for _ in range(n)]
    if n > 1:
        g[1][0] = "#"
    if m > 1:
        g[0][1] = "#"
elif mode == "detour":
    # 첫 행은 오른쪽 끝까지 열고, 마지막 열을 따라 내려온다. 첫 열도 열어 둔다(짧은 길).
    g = [["#"] * m for _ in range(n)]
    for c in range(m):
        g[0][c] = "."
    for r in range(n):
        g[r][m - 1] = "."
        g[r][0] = "."
    for c in range(m):
        g[n - 1][c] = "."
elif mode == "corner":
    g = [["#"] * m for _ in range(n)]
    for i in range(min(n, m)):
        g[i][i] = "."
g[0][0] = g[n - 1][m - 1] = "."
sys.stdout.write(f"{n} {m}\n" + "".join("".join(row) + "\n" for row in g))
