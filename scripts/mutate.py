#!/usr/bin/env python3
"""정답(sol/main.cpp)을 한 곳씩 바꾼 변이 풀이로 TC의 구멍을 찾는다.

사용: python3 scripts/mutate.py <문제 폴더> --gen "<gen.py 인자, {seed} 자리에 시드>" [--gen ...] [--count 100]

변이마다 TC 전체(examples, tests)를 돌린다. TC를 모두 통과한 변이는 생성기로 만든 작은 입력에서
sol/brute.cpp와 대조한다 (stress.py와 같은 방식, --gen에는 stress에 쓰는 작은 입력 인자를 준다).
  - 대조에서 틀리면 TC 구멍이다. 결과가 갈린 입력 중 가장 작은 것의 생성 인자를 알려 준다.
    그 인자 줄을 gen/tests.txt에 더하면 이 변이를 잡는 TC가 된다.
    변이 코드는 .build/mutate/hole-<n>.cpp에 남긴다 (sol/wrong_answer/에 옮겨 회귀 확인용으로 쓴다).
  - 대조에서도 같으면 정답과 결과가 같은 변이일 가능성이 크다 (동등 추정). 사람이 한 번 훑어본다.
# 줄(전처리), // 주석, 문자열 안은 바꾸지 않는다 (scanf/printf의 %lld만 예외).

출력 줄(고정 문구):
  컴파일 에러: sol/main.cpp
  변이: <n>개 (컴파일 안 되는 변이 <c>개 제외)
  TC가 잡음: <k>/<n>
  TC 구멍: L<줄>:<열> '<옛>'→'<새>' — <gen 인자에 시드를 넣은 것> (.build/mutate/hole-<i>.cpp)
  동등 추정: L<줄>:<열> '<옛>'→'<새>'
  결과: TC 구멍 <h>개, 동등 추정 <e>개
종료 코드: TC 구멍이 없으면 0, 있으면 1
"""
import argparse
import re
import shlex
import subprocess
import sys
from pathlib import Path

from judge import OK, compile_solution, execute, is_correct, judge, list_cases, load_meta

CAP_SEC = 5
DEFAULT_TL = 1.0

# (찾을 패턴, 바꿀 문자열). 학생이 흔히 내는 한 글자 실수.
RULES = [
    (r"<=", "<"), (r"(?<![<-])<(?![<=])", "<="), (r">=", ">"), (r"(?<![->])>(?![>=])", ">="),
    (r"==", "!="), (r"!=", "=="), (r"&&", "||"), (r"\|\|", "&&"),
    (r"\+ 1\b", ""), (r"- 1\b", ""), (r"\+ 1\b", "+ 2"), (r"- 1\b", "- 2"),
    (r"\blong long\b", "int"), (r"%lld", "%d"),
    (r"\bmax\b", "min"), (r"\bmin\b", "max"), (r"\b0\b", "1"), (r"\b1\b", "0"),
    (r"\+\+", "--"),
]
STRING = re.compile(r'"(?:\\.|[^"\\])*"')


def mutants(src: str):
    """(줄 번호, 열 번호, 옛, 새, 변이 코드)를 낸다."""
    offset = 0
    lines = src.split("\n")
    for lineno, line in enumerate(lines, 1):
        start = offset
        offset += len(line) + 1
        code = line.split("//")[0]
        if code.lstrip().startswith("#"):
            continue
        strings = [m.span() for m in STRING.finditer(code)]
        for pat, rep in RULES:
            for m in re.finditer(pat, code):
                in_string = any(a <= m.start() < b for a, b in strings)
                if in_string != (pat == r"%lld"):
                    continue
                a, b = start + m.start(), start + m.end()
                yield lineno, m.start() + 1, m.group(), rep, src[:a] + rep + src[b:]


def gen_input(root: Path, gen_args: str, seed: int):
    argv = shlex.split(gen_args.replace("{seed}", str(seed)))
    g = subprocess.run([sys.executable, str(root / "gen" / "gen.py"), *argv], capture_output=True, timeout=60)
    return g.stdout if g.returncode == 0 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("problem")
    ap.add_argument("--gen", action="append", required=True)
    ap.add_argument("--count", type=int, default=100)
    args = ap.parse_args()
    root = Path(args.problem)
    meta = load_meta(root)
    tl = meta["time_limit_ms"] / 1000 or DEFAULT_TL
    mem = meta["memory_mb"]
    work = root / ".build" / "mutate"
    work.mkdir(parents=True, exist_ok=True)
    for old in work.glob("hole-*.cpp"):
        old.unlink()

    if compile_solution(root, root / "sol" / "main.cpp") is None:
        print("컴파일 에러: sol/main.cpp")
        sys.exit(1)
    brute = compile_solution(root, root / "sol" / "brute.cpp")
    if brute is None:
        print("컴파일 에러: sol/brute.cpp")
        sys.exit(1)
    cases = list_cases(root)

    # 작은 입력과 brute 출력은 변이마다 다시 만들지 않는다
    small = []
    for gen_args in args.gen:
        for seed in range(1, args.count + 1):
            data = gen_input(root, gen_args, seed)
            if data is None:
                continue
            inp = work / f"small-{len(small)}.in"
            inp.write_bytes(data)
            status, _, out, _ = execute(brute, inp, CAP_SEC, mem)
            if status != OK:
                continue
            ans = inp.with_suffix(".out")
            ans.write_bytes(out)
            small.append((len(data), gen_args.replace("{seed}", str(seed)), inp, ans))
    small.sort(key=lambda s: s[0])

    src = (root / "sol" / "main.cpp").read_text(encoding="utf-8")
    total = broken = killed = 0
    holes, same = [], []
    for lineno, col, old, new, code in mutants(src):
        mfile = work / "mutant.cpp"
        exe = work / "mutant"
        mfile.write_text(code, encoding="utf-8")
        r = subprocess.run(["g++", "-O2", "-std=gnu++17", "-w", "-o", str(exe), str(mfile)],
                           capture_output=True)
        if r.returncode != 0:
            broken += 1
            continue
        total += 1
        cmd = [str(exe)]
        if any(judge(root, cmd, inp, tl, mem)[0] != OK for inp in cases):
            killed += 1
            continue
        desc = f"L{lineno}:{col} '{old}'→'{new}'"
        for _, gen_line, inp, ans in small:  # 작은 입력부터
            status, _, out, _ = execute(cmd, inp, CAP_SEC, mem)
            if status != OK or not is_correct(root, inp, out, ans):
                hole = work / f"hole-{len(holes) + 1}.cpp"
                hole.write_text(f"// 변이 {desc}: TC를 모두 통과하지만 틀림\n{code}", encoding="utf-8")
                holes.append(f"TC 구멍: {desc} — {gen_line} (.build/mutate/{hole.name})")
                break
        else:
            same.append(f"동등 추정: {desc}")

    print(f"변이: {total}개 (컴파일 안 되는 변이 {broken}개 제외)")
    print(f"TC가 잡음: {killed}/{total}")
    for line in holes + same:
        print(line)
    print(f"결과: TC 구멍 {len(holes)}개, 동등 추정 {len(same)}개")
    sys.exit(1 if holes else 0)


if __name__ == "__main__":
    main()
