#!/usr/bin/env python3
"""입력 검사(validator)와 TC 파일 형식을 검사한다.

사용: python3 scripts/validate.py <문제 폴더>

하는 일:
  1. examples/, tests/의 모든 .in이 validator를 통과하는지
  2. invalid/의 모든 .in을 validator가 거부하는지
  3. 정상 입력을 조금씩 망가뜨린 변형(줄 끝 공백, 선행 0 등)을 validator가 거부하는지
  4. 모든 .in/.out이 \\n으로 끝나고 CR·줄 끝 공백이 없는지, 같은 입력이 중복되지 않는지
  5. checker.py가 있으면: 정답 파일을 정답으로 보는지, 이상한 출력에 죽지 않는지
  6. 변수별로 TC 전체에서 실제 나온 범위를 모아 출력

출력 줄(고정 문구):
  validator 거부: <TC> — <validator 메시지>
  validator 오류: <대상> (종료 코드 <n>)    (0도 43도 아닌 종료. 예외로 죽은 것)
  거부 안 함: <invalid 파일>
  거부 안 함: <변형 이름> (<원본 TC>)
  형식 문제: <파일> <내용>
  중복 입력: <TC> = <TC>
  checker가 정답을 거부: <TC>
  checker 오류: 출력 <값> (종료 코드 <n>)
  범위: <변수> <최소> <최대>        (정보. 문제로 세지 않음)
  검증: 정상 | 검증: 문제 <n>개
종료 코드: 정상 0, 문제 있음 1
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from judge import CHECKER_WA, list_cases
from vlib import REJECT

SCRIPTS = Path(__file__).resolve().parent
MUTANT_SOURCES = 3  # 변형을 만들 원본 TC 개수

JUNK_OUTPUTS = [b"", b"-1\n", b"2147483648\n", b"9223372036854775808\n",
                b"NaN\n", b"inf\n", b"\x00\n", b"1/0\n", b"abc\n"]


def mutants(data: bytes):
    """(변형 이름, 변형된 입력). 엄격한 validator라면 전부 거부해야 한다."""
    out = [("빈 파일", b""), ("끝에 쓰레기", data + b"x\n"), ("빈 줄 추가", data + b"\n")]
    if b"\n" in data:
        out.append(("줄 끝 공백", data.replace(b"\n", b" \n", 1)))
        out.append(("CRLF 줄바꿈", data.replace(b"\n", b"\r\n")))
    if data.endswith(b"\n"):
        out.append(("마지막 개행 없음", data[:-1]))
    if b" " in data:
        out.append(("공백 두 칸", data.replace(b" ", b"  ", 1)))
    m = re.search(rb"(?<![0-9.])[0-9]+", data)
    if m:
        out.append(("선행 0", data[:m.start()] + b"0" + data[m.start():]))
    return out


def run_validator(root: Path, data: bytes):
    env = dict(os.environ, PYTHONPATH=str(SCRIPTS))
    r = subprocess.run([sys.executable, str(root / "validator.py")], input=data,
                       capture_output=True, env=env, timeout=60)
    return r.returncode, r.stdout.decode("utf-8", "replace")


def format_problems(root: Path, f: Path):
    data = f.read_bytes()
    name = f"{f.parent.name}/{f.name}"
    out = []
    if b"\r" in data:
        out.append(f"형식 문제: {name} CR 문자")
    if data and not data.endswith(b"\n"):
        out.append(f"형식 문제: {name} 마지막 개행 없음")
    for i, line in enumerate(data.split(b"\n"), 1):
        if line != line.rstrip(b" \t"):
            out.append(f"형식 문제: {name} 줄 끝 공백 (줄 {i})")
            break
    return out


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    root = Path(sys.argv[1])
    problems = []
    ranges = {}

    if not (root / "validator.py").is_file():
        print("없음: validator.py")
        print("검증: 문제 1개")
        sys.exit(1)

    cases = list_cases(root)
    valid = []
    for inp in cases:
        name = f"{inp.parent.name}/{inp.name}"
        code, out = run_validator(root, inp.read_bytes())
        if code not in (0, REJECT):
            problems.append(f"validator 오류: {name} (종료 코드 {code})")
            continue
        if code != 0:
            msg = out.strip().splitlines()[-1] if out.strip() else f"종료 코드 {code}"
            problems.append(f"validator 거부: {name} — {msg}")
            continue
        valid.append(inp)
        for line in out.splitlines():
            parts = line.split()
            if len(parts) == 4 and parts[0] == "범위:":
                var, lo, hi = parts[1], int(parts[2]), int(parts[3])
                old = ranges.get(var, (lo, hi))
                ranges[var] = (min(old[0], lo), max(old[1], hi))

    def expect_reject(data, label):
        code = run_validator(root, data)[0]
        if code == 0:
            problems.append(f"거부 안 함: {label}")
        elif code != REJECT:
            problems.append(f"validator 오류: {label} (종료 코드 {code})")

    for inp in sorted((root / "invalid").glob("*.in")):
        expect_reject(inp.read_bytes(), f"invalid/{inp.name}")

    for inp in valid[:MUTANT_SOURCES]:
        for desc, data in mutants(inp.read_bytes()):
            expect_reject(data, f"{desc} ({inp.parent.name}/{inp.name})")

    seen = {}
    for inp in cases:
        problems += format_problems(root, inp)
        ans = inp.with_suffix(".out")
        if ans.is_file():
            problems += format_problems(root, ans)
        key = inp.read_bytes()
        name = f"{inp.parent.name}/{inp.name}"
        if key in seen:
            problems.append(f"중복 입력: {name} = {seen[key]}")
        else:
            seen[key] = name

    checker = root / "checker.py"
    if checker.is_file() and cases:
        with tempfile.TemporaryDirectory() as d:
            junk = Path(d) / "out"
            for inp in cases:
                ans = inp.with_suffix(".out")
                if not ans.is_file():
                    continue
                r = subprocess.run([sys.executable, str(checker), str(inp), str(ans), str(ans)],
                                   capture_output=True)
                if r.returncode != 0:
                    problems.append(f"checker가 정답을 거부: {inp.parent.name}/{inp.name}")
            inp = cases[0]
            for j in JUNK_OUTPUTS:
                junk.write_bytes(j)
                r = subprocess.run([sys.executable, str(checker), str(inp), str(junk),
                                    str(inp.with_suffix(".out"))], capture_output=True)
                if r.returncode not in (0, CHECKER_WA):
                    problems.append(f"checker 오류: 출력 {j!r} (종료 코드 {r.returncode})")

    for line in problems:
        print(line)
    for var in sorted(ranges):
        print(f"범위: {var} {ranges[var][0]} {ranges[var][1]}")
    print("검증: 정상" if not problems else f"검증: 문제 {len(problems)}개")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
