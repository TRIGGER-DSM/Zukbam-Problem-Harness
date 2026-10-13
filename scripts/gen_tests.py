#!/usr/bin/env python3
"""gen/tests.txt의 명령대로 숨은 TC 입력을 만든다.

사용: python3 scripts/gen_tests.py <문제 폴더> [--start K]

gen/tests.txt는 한 줄에 gen/gen.py의 인자 하나씩이다 (빈 줄과 #으로 시작하는 줄은 건너뜀).
i번째 명령의 결과를 tests/<K+i-1>.in에 쓴다 (기본 K=1). 사용자가 준 TC가 있으면 K를 그 다음 번호로 준다.
같은 인자로 두 번 실행해 결과가 같은지(재현 가능한지)도 확인한다.
입력 내용이 바뀌면 짝인 .out은 낡은 것이므로 지운다 (make_outputs.py로 다시 만든다).

출력 줄(고정 문구):
  생성: tests/<n>.in (<인자>)
  이전 출력 삭제: tests/<n>.out
  생성 실패: 줄 <n> (종료 코드 <c>)
  비결정적: 줄 <n> (<인자>)
  결과: 생성 <k>개, 문제 <m>개
종료 코드: 문제 없음 0, 있음 1
"""
import argparse
import shlex
import subprocess
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("problem")
    ap.add_argument("--start", type=int, default=1)
    args = ap.parse_args()
    root = Path(args.problem)
    gen = root / "gen" / "gen.py"
    lines = (root / "gen" / "tests.txt").read_text(encoding="utf-8").splitlines()
    (root / "tests").mkdir(exist_ok=True)

    made = bad = 0
    num = args.start
    for lineno, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        cmd = [sys.executable, str(gen), *shlex.split(line)]
        first = subprocess.run(cmd, capture_output=True, timeout=120)
        if first.returncode != 0:
            print(f"생성 실패: 줄 {lineno} (종료 코드 {first.returncode})")
            bad += 1
            continue
        second = subprocess.run(cmd, capture_output=True, timeout=120)
        if second.stdout != first.stdout:
            print(f"비결정적: 줄 {lineno} ({line})")
            bad += 1
        inp = root / "tests" / f"{num}.in"
        out = inp.with_suffix(".out")
        if out.exists() and (not inp.exists() or inp.read_bytes() != first.stdout):
            out.unlink()
            print(f"이전 출력 삭제: tests/{num}.out")
        inp.write_bytes(first.stdout)
        print(f"생성: tests/{num}.in ({line})")
        made += 1
        num += 1

    print(f"결과: 생성 {made}개, 문제 {bad}개")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
