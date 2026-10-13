#!/usr/bin/env python3
"""모든 풀이를 TC 전체에 돌려 기대 판정을 받는지, 시간 제한이 적절한지 검사한다.

사용: python3 scripts/verdicts.py <문제 폴더>

기대 판정과 시간 제한 공식은 rules/package.md를 따른다.
  - 정답(sol/main.cpp, sol/main.py, sol/accepted/*): 모든 TC 통과
  - sol/wrong_answer/*: 통과·오답만, 오답 1개 이상
  - sol/time_limit_exceeded/*: 통과·시간 초과만, 시간 초과 1개 이상
  - sol/runtime_error/*: 통과·런타임 에러만, 런타임 에러 1개 이상
  - T_ac × 2 ≤ 시간 제한, 시간 제한 × 1.5 ≤ T_tle
시간은 시간 제한의 3배까지 재서 T_ac, T_tle를 구한다. 정답 풀이는 TC마다 최대 3번 재서 가장 짧은 값을 쓴다
(다른 작업이 CPU를 나눠 쓰면 측정값이 두 배 넘게 부풀 수 있다). time_limit_ms가 0이면 1000ms 기준으로 잰다.

출력 줄(고정 문구):
  시간 제한 미정: 1000ms 기준으로 측정
  풀이: <경로> — <판정별 개수>, 최대 <초>s
  기대와 다름: <경로> — <이유>
  컴파일 에러: <경로>
  T_ac: <초>s (<경로>)
  T_tle: <초>s (<경로>) | T_tle: <초>s 이상 (<경로>) | T_tle: 없음
  시간 제한 조건 만족: T_ac×2 = <a>s ≤ <TL>s ≤ T_tle/1.5 = <b>s
  시간 제한 문제: <내용>
  추천 시간 제한: <ms>ms | 추천 시간 제한: 없음
  판정: 정상 | 판정: 문제 <n>개
종료 코드: 정상 0, 문제 있음 1
"""
import math
import sys
from collections import Counter
from pathlib import Path

from judge import OK, RTE, TLE, WA, compile_solution, judge, list_cases, load_meta, rel

MEASURE = 3          # 시간 제한의 몇 배까지 재는지
AC_REPEAT = 3        # 정답 풀이를 TC마다 몇 번 재서 최솟값을 쓰는지
REPEAT_ABOVE = 0.05  # 이보다 오래 걸린 TC만 다시 잰다 (초)
DEFAULT_TL = 1.0     # time_limit_ms가 0일 때 측정 기준 (초)
RESOLUTION_MS = 500  # 추천 시간 제한 단위
AC_FACTOR, TLE_FACTOR = 2.0, 1.5

GROUPS = [  # (폴더, 허용 판정, 필수 판정)
    ("accepted", {OK}, None),
    ("wrong_answer", {OK, WA}, WA),
    ("time_limit_exceeded", {OK, TLE}, TLE),
    ("runtime_error", {OK, RTE}, RTE),
]


def solutions(root: Path):
    sol = root / "sol"
    out = [("accepted", sol / name) for name in ("main.cpp", "main.py") if (sol / name).is_file()]
    for group, _, _ in GROUPS:
        d = sol / group
        if d.is_dir():
            out += [(group, f) for f in sorted(d.iterdir()) if f.suffix in (".cpp", ".py")]
    return out


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    root = Path(sys.argv[1])
    meta = load_meta(root)
    tl = meta["time_limit_ms"] / 1000
    mem = meta["memory_mb"]
    if tl <= 0:
        print("시간 제한 미정: 1000ms 기준으로 측정")
        tl = DEFAULT_TL
    cases = list_cases(root)
    rules = {g: (allowed, required) for g, allowed, required in GROUPS}
    problems = []
    t_ac = (0.0, None)
    t_tle = (math.inf, None)

    for group, path in solutions(root):
        name = rel(root, path)
        cmd = compile_solution(root, path)
        if cmd is None:
            print(f"컴파일 에러: {name}")
            problems.append(name)
            continue
        counts = Counter()
        first = {}
        slowest = 0.0
        for inp in cases:
            # 시간 초과 풀이는 한 번 측정 한도에 닿으면 나머지는 시간 제한까지만 돌린다
            cap = tl * MEASURE
            if group == "time_limit_exceeded" and slowest >= cap:
                cap = tl
            verdict, used, _ = judge(root, cmd, inp, tl, mem, cap_sec=cap)
            if group == "accepted" and verdict in (OK, TLE) and used > REPEAT_ABOVE:
                for _ in range(AC_REPEAT - 1):
                    again, t, _ = judge(root, cmd, inp, tl, mem, cap_sec=cap)
                    if again == OK and t < used:
                        verdict, used = OK, t
            counts[verdict] += 1
            first.setdefault(verdict, f"{inp.parent.name}/{inp.name}")
            slowest = max(slowest, used)
        summary = ", ".join(f"{v} {counts[v]}" for v in (OK, WA, TLE, RTE) if counts[v])
        print(f"풀이: {name} — {summary}, 최대 {slowest:.3f}s")

        allowed, required = rules[group]
        reasons = [f"{v} ({first[v]})" for v in (OK, WA, TLE, RTE) if counts[v] and v not in allowed]
        if reasons:
            problems.append(f"기대와 다름: {name} — 허용되지 않는 판정 " + ", ".join(reasons))
        elif required and not counts[required]:
            problems.append(f"기대와 다름: {name} — {required}이(가) 한 번도 안 나옴")

        if group == "accepted" and slowest > t_ac[0]:
            t_ac = (slowest, name)
        if group == "time_limit_exceeded" and counts[TLE] and slowest < t_tle[0]:
            t_tle = (slowest, name)

    for p in problems:
        if p.startswith("기대와 다름"):
            print(p)

    print(f"T_ac: {t_ac[0]:.3f}s ({t_ac[1]})")
    if t_tle[1] is None:
        print("T_tle: 없음")
    elif t_tle[0] >= tl * MEASURE:
        print(f"T_tle: {t_tle[0]:.3f}s 이상 ({t_tle[1]})")
    else:
        print(f"T_tle: {t_tle[0]:.3f}s ({t_tle[1]})")

    low, high = t_ac[0] * AC_FACTOR, t_tle[0] / TLE_FACTOR
    if low <= tl <= high:
        print(f"시간 제한 조건 만족: T_ac×2 = {low:.3f}s ≤ {tl:.3f}s ≤ T_tle/1.5 = {high:.3f}s")
    else:
        if low > tl:
            problems.append(f"시간 제한 문제: T_ac×2 = {low:.3f}s > 시간 제한 {tl:.3f}s")
        if tl > high:
            problems.append(f"시간 제한 문제: 시간 제한 {tl:.3f}s > T_tle/1.5 = {high:.3f}s")
        for p in problems:
            if p.startswith("시간 제한 문제"):
                print(p)

    rec = max(1, math.ceil(low * 1000 / RESOLUTION_MS)) * RESOLUTION_MS
    if rec / 1000 <= high:
        print(f"추천 시간 제한: {rec}ms")
    else:
        print("추천 시간 제한: 없음")

    print("판정: 정상" if not problems else f"판정: 문제 {len(problems)}개")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
