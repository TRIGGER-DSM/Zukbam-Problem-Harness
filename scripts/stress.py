#!/usr/bin/env python3
"""두 풀이를 생성기로 만든 랜덤 입력에서 대조한다 (기본: sol/main.cpp vs sol/brute.cpp).

사용: python3 scripts/stress.py <문제 폴더> --gen "<gen.py 인자, {seed} 자리에 시드>" [--gen ...]
        [--count 200] [--a sol/main.cpp] [--b sol/brute.cpp]

--gen을 여러 번 주면 각각 --count번씩 돌린다. 생성된 입력은 validator로도 검사한다.
결과가 갈린 입력 중 가장 작은 것을 .build/stress/smallest.in에 저장하고 내용을 보여준다.

출력 줄(고정 문구):
  생성 실패: <gen 인자> seed <s>
  생성 입력 제약 위반: <gen 인자> seed <s> — <validator 메시지>
  실행 실패: <A|B> <gen 인자> seed <s> (<시간 초과|런타임 에러>)
  불일치: <n>건, 가장 작은 입력 <b>바이트 (<gen 인자> seed <s>)
  결과: 일치 <k>/<n>
종료 코드: 전부 일치하고 실패가 없으면 0, 아니면 1
"""
import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path

from judge import OK, compile_solution, execute, is_correct, load_meta
from vlib import REJECT

SCRIPTS = Path(__file__).resolve().parent
CAP_SEC = 10
SHOW_LINES = 15


def show(title, data: bytes):
    lines = data.decode("utf-8", "replace").splitlines()
    print(f"--- {title} ---")
    for line in lines[:SHOW_LINES]:
        print(line[:200])
    if len(lines) > SHOW_LINES:
        print(f"... ({len(lines)}줄 중 {SHOW_LINES}줄)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("problem")
    ap.add_argument("--gen", action="append", required=True)
    ap.add_argument("--count", type=int, default=200)
    ap.add_argument("--a", default="sol/main.cpp")
    ap.add_argument("--b", default="sol/brute.cpp")
    args = ap.parse_args()
    root = Path(args.problem)
    meta = load_meta(root)
    work = root / ".build" / "stress"
    work.mkdir(parents=True, exist_ok=True)
    inp = work / "case.in"

    cmds = {}
    for label, path in (("A", args.a), ("B", args.b)):
        cmds[label] = compile_solution(root, root / path)
        if cmds[label] is None:
            print(f"컴파일 에러: {path}")
            sys.exit(1)

    env = dict(os.environ, PYTHONPATH=str(SCRIPTS))
    has_validator = (root / "validator.py").is_file()
    total = agree = failures = 0
    smallest = None  # (크기, gen, seed, 입력, A 출력, B 출력)
    mismatches = 0

    for gen_args in args.gen:
        for seed in range(1, args.count + 1):
            total += 1
            argv = shlex.split(gen_args.replace("{seed}", str(seed)))
            g = subprocess.run([sys.executable, str(root / "gen" / "gen.py"), *argv],
                               capture_output=True, timeout=60)
            if g.returncode != 0:
                print(f"생성 실패: {gen_args} seed {seed}")
                failures += 1
                continue
            data = g.stdout
            inp.write_bytes(data)
            if has_validator:
                v = subprocess.run([sys.executable, str(root / "validator.py")], input=data,
                                   capture_output=True, env=env, timeout=60)
                if v.returncode != 0:
                    msg = v.stdout.decode("utf-8", "replace").strip()
                    if v.returncode != REJECT:
                        msg = f"validator 오류 (종료 코드 {v.returncode})"
                    print(f"생성 입력 제약 위반: {gen_args} seed {seed} — {msg}")
                    failures += 1
                    continue
            outs = {}
            for label in ("A", "B"):
                status, _, out, _ = execute(cmds[label], inp, CAP_SEC, meta["memory_mb"])
                if status != OK:
                    print(f"실행 실패: {label} {gen_args} seed {seed} ({status})")
                    failures += 1
                    break
                outs[label] = out
            if len(outs) < 2:
                continue
            ans = work / "case.out"
            ans.write_bytes(outs["B"])
            if is_correct(root, inp, outs["A"], ans):
                agree += 1
                continue
            mismatches += 1
            if smallest is None or len(data) < smallest[0]:
                smallest = (len(data), gen_args, seed, data, outs["A"], outs["B"])

    if smallest:
        size, gen_args, seed, data, a_out, b_out = smallest
        (work / "smallest.in").write_bytes(data)
        print(f"불일치: {mismatches}건, 가장 작은 입력 {size}바이트 ({gen_args} seed {seed})")
        show("입력", data)
        show(f"A 출력 ({args.a})", a_out)
        show(f"B 출력 ({args.b})", b_out)
    print(f"결과: 일치 {agree}/{total}")
    sys.exit(0 if agree == total else 1)


if __name__ == "__main__":
    main()
