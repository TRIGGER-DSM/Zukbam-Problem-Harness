#!/usr/bin/env python3
"""문제 패키지의 형식을 검사한다.

사용: python3 scripts/check_package.py <문제 폴더>

출력 줄(고정 문구):
  없음: <경로>
  meta.json 문제: <필드>
  짝 없음: <경로>
  패키지: 정상 | 패키지: 문제 <n>개
종료 코드: 정상 0, 문제 있음 1
"""
import json
import sys
from pathlib import Path

REQUIRED_FILES = ["problem.md", "meta.json", "state.md"]
TC_DIRS = ["examples", "tests"]


def check_meta(meta):
    """잘못된 필드 이름 목록을 돌려준다."""
    bad = []
    if not isinstance(meta.get("title"), str) or not meta.get("title"):
        bad.append("title")
    if not isinstance(meta.get("method"), str):
        bad.append("method")
    if not isinstance(meta.get("keywords"), list):
        bad.append("keywords")
    if not isinstance(meta.get("difficulty"), str):
        bad.append("difficulty")
    for key in ("time_limit_ms", "memory_mb"):
        v = meta.get(key)
        if not isinstance(v, int) or isinstance(v, bool) or v <= 0:
            bad.append(key)
    if meta.get("mode") not in (1, 2, 3):
        bad.append("mode")
    return bad


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    root = Path(sys.argv[1])
    problems = []

    for name in REQUIRED_FILES:
        if not (root / name).is_file():
            problems.append(f"없음: {name}")

    meta_path = root / "meta.json"
    if meta_path.is_file():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            problems.append("meta.json 문제: JSON 형식 오류")
        else:
            problems += [f"meta.json 문제: {key}" for key in check_meta(meta)]

    for d in TC_DIRS:
        tc_dir = root / d
        if not tc_dir.is_dir():
            problems.append(f"없음: {d}/")
            continue
        ins = {f.stem for f in tc_dir.glob("*.in")}
        outs = {f.stem for f in tc_dir.glob("*.out")}
        problems += [f"짝 없음: {d}/{s}.in" for s in sorted(ins - outs)]
        problems += [f"짝 없음: {d}/{s}.out" for s in sorted(outs - ins)]

    for line in problems:
        print(line)
    print("패키지: 정상" if not problems else f"패키지: 문제 {len(problems)}개")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
