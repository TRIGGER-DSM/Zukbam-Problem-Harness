#!/usr/bin/env python3
"""주 정답(sol/main.cpp)을 실행해 .out을 만들거나, 이미 있는 .out과 비교한다.

사용: python3 scripts/make_outputs.py <문제 폴더> [--overwrite]

- tests/의 .in 중 .out이 없는 것: 정답을 실행해 .out을 쓴다
- .out이 이미 있는 것(예제, 사용자가 준 TC): 덮어쓰지 않고 정답 출력과 비교한다
- --overwrite: tests/의 .out을 모두 다시 쓴다 (examples/는 절대 덮어쓰지 않는다)
- 예제 .out은 출제자가 준다. 단 AI가 만든 문제(meta.json의 mode가 1)는 없는 예제 .out도 정답으로 만든다
시간 제한은 보지 않는다(최대 60초). 시간 제한 검사는 verdicts.py가 한다.

출력 줄(고정 문구):
  작성: <TC .out>
  정답과 다름: <TC>
  실행 실패: <TC> (<시간 초과|런타임 에러>)
  예제 출력 없음: <TC>          (mode가 1이 아니면 예제 .out을 만들지 않는다)
  컴파일 에러: sol/main.cpp
  결과: 작성 <a>, 일치 <b>, 다름 <c>, 실패 <d>
종료 코드: 다름·실패가 없으면 0, 있으면 1
"""
import argparse
import sys
from pathlib import Path

from judge import OK, compile_solution, execute, is_correct, list_cases, load_meta

GEN_CAP_SEC = 60


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("problem")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()
    root = Path(args.problem)
    meta = load_meta(root)

    cmd = compile_solution(root, root / "sol" / "main.cpp")
    if cmd is None:
        print("컴파일 에러: sol/main.cpp")
        sys.exit(1)

    wrote = same = diff = failed = 0
    for inp in list_cases(root):
        name = f"{inp.parent.name}/{inp.name}"
        ans = inp.with_suffix(".out")
        if inp.parent.name == "examples" and not ans.is_file() and meta.get("mode") != 1:
            print(f"예제 출력 없음: {name}")
            failed += 1
            continue
        status, _, out, _ = execute(cmd, inp, GEN_CAP_SEC, meta["memory_mb"])
        if status != OK:
            print(f"실행 실패: {name} ({status})")
            failed += 1
            continue
        if ans.is_file() and not (args.overwrite and inp.parent.name == "tests"):
            if is_correct(root, inp, out, ans):
                same += 1
            else:
                print(f"정답과 다름: {name}")
                diff += 1
            continue
        ans.write_bytes(out)
        print(f"작성: {inp.parent.name}/{ans.name}")
        wrote += 1

    print(f"결과: 작성 {wrote}, 일치 {same}, 다름 {diff}, 실패 {failed}")
    sys.exit(1 if diff or failed else 0)


if __name__ == "__main__":
    main()
