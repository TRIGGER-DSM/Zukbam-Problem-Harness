"""사용: gen.py <n> <q> <모드> <seed>
모드: random   a_i는 [-10^9, 10^9], 구간은 랜덤
      small    a_i는 [-5, 5] (손으로 따라가기 쉬움)
      max      a_i는 전부 10^9 (합이 int를 넘음)
      min      a_i는 전부 -10^9
      full     구간이 전부 [1, n] (단순 반복 풀이가 가장 느린 경우)
      point    구간이 전부 길이 1 (l == r)
"""
import random
import sys

n, q, mode, seed = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4]
rnd = random.Random(f"{n} {q} {mode} {seed}")

if mode == "small":
    a = [rnd.randint(-5, 5) for _ in range(n)]
elif mode == "max":
    a = [10**9] * n
elif mode == "min":
    a = [-10**9] * n
else:
    a = [rnd.randint(-10**9, 10**9) for _ in range(n)]

out = [f"{n} {q}", " ".join(map(str, a))]
for _ in range(q):
    if mode == "full":
        l, r = 1, n
    elif mode == "point":
        l = r = rnd.randint(1, n)
    else:
        l, r = sorted((rnd.randint(1, n), rnd.randint(1, n)))
    out.append(f"{l} {r}")
sys.stdout.write("\n".join(out) + "\n")
