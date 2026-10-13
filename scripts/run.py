#!/usr/bin/env python3
"""풀이 하나를 문제 패키지의 TC로 채점한다.

사용: python3 scripts/run.py <문제 폴더> <풀이 파일(.cpp|.py)> [--set examples|tests|all]

시간 제한과 메모리 제한은 <문제 폴더>/meta.json의 time_limit_ms, memory_mb를 쓴다.
시간은 자식 프로세스의 CPU 시간(user+sys)으로 잰다. checker.py가 있으면 그것으로 판정하고,
없으면 줄 끝 공백과 마지막 빈 줄을 무시한 정확 일치로 비교한다.

출력 줄(고정 문구):
  컴파일 에러: <풀이 경로>
  통과: <TC> (<초>s)
  오답: <TC> (<초>s)
  시간 초과: <TC>
  런타임 에러: <TC> (종료 코드 <n>)
  결과: 통과 <k>/<n>
종료 코드: 전부 통과 0, 아니면 1, 사용 오류 2
"""
import argparse
import sys
from pathlib import Path

from judge import OK, RTE, TLE, compile_solution, judge, list_cases, load_meta, rel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("problem")
    ap.add_argument("solution")
    ap.add_argument("--set", choices=["examples", "tests", "all"], default="all")
    args = ap.parse_args()

    root = Path(args.problem)
    sol = Path(args.solution)
    meta = load_meta(root)
    tl = meta["time_limit_ms"] / 1000
    sets = ("examples", "tests") if args.set == "all" else (args.set,)
    cases = list_cases(root, sets)

    try:
        cmd = compile_solution(root, sol)
    except ValueError as e:
        print(e)
        sys.exit(2)
    if cmd is None:
        print(f"컴파일 에러: {rel(root, sol)}")
        sys.exit(1)

    passed = 0
    for inp in cases:
        name = f"{inp.parent.name}/{inp.name}"
        verdict, used, code = judge(root, cmd, inp, tl, meta["memory_mb"])
        if verdict == OK:
            passed += 1
            print(f"통과: {name} ({used:.3f}s)")
        elif verdict == TLE:
            print(f"시간 초과: {name}")
        elif verdict == RTE:
            print(f"런타임 에러: {name} (종료 코드 {code})")
        else:
            print(f"오답: {name} ({used:.3f}s)")

    print(f"결과: 통과 {passed}/{len(cases)}")
    sys.exit(0 if cases and passed == len(cases) else 1)


if __name__ == "__main__":
    main()
