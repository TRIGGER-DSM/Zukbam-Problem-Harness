"""사용: gen.py <n> <모드> <seed>
모드: random   시작·길이 랜덤 (좌표 최대 10^9)
      small    좌표 [0, 20] (손으로 따라가기 쉬움, 겹침·맞닿음이 많음)
      touch    끝과 시작이 맞닿은 사슬 (맞닿음을 겹침으로 보는 풀이를 잡음)
      nested   먼저 시작해 전체를 덮는 긴 신청 + 그 안의 짧은 신청들 (시작 순 그리디를 잡음)
      bridge   [10k, 10k+10) 사슬 사이에 짧은 다리 [10k+9, 10k+11) (길이 순 그리디를 잡음)
      same     모두 같은 구간
"""
import random
import sys

n, mode, seed = int(sys.argv[1]), sys.argv[2], sys.argv[3]
rnd = random.Random(f"{n} {mode} {seed}")
LIM = 10**9
iv = []
if mode == "small":
    for _ in range(n):
        s = rnd.randint(0, 19)
        iv.append((s, rnd.randint(s + 1, 20)))
elif mode == "touch":
    step = LIM // n
    iv = [(i * step, (i + 1) * step) for i in range(n)]
elif mode == "nested":
    iv.append((0, LIM))
    step = (LIM - 1) // (n - 1) if n > 1 else 1
    iv += [(1 + i * step, 1 + (i + 1) * step) for i in range(n - 1)]
elif mode == "bridge":
    k = 0
    while len(iv) < n:
        iv.append((10 * k, 10 * k + 10))
        if len(iv) < n:
            iv.append((10 * k + 9, 10 * k + 11))
        k += 1
elif mode == "same":
    s = rnd.randint(0, LIM - 1)
    e = rnd.randint(s + 1, LIM)
    iv = [(s, e)] * n
else:
    for _ in range(n):
        s = rnd.randint(0, LIM - 1)
        iv.append((s, min(LIM, s + rnd.randint(1, LIM // max(1, n // 10)))))
rnd.shuffle(iv)
sys.stdout.write(f"{n}\n" + "".join(f"{s} {e}\n" for s, e in iv))
