#!/usr/bin/env python3
"""평가 세트를 채점한다: 정상 문제에서 오탐이 없는지, 결함 케이스를 스크립트가 잡는지.

사용: python3 eval/run_eval.py [케이스 이름 ...] [--skip-base]

eval/base/<문제>/      정상 문제 (TC는 git에 넣지 않고 매번 gen/tests.txt로 만든다)
eval/cases/<이름>.json  결함 케이스
  base       바탕 문제
  item       체크리스트 항목 (docs/research/checklist.md)
  detector   script(스크립트가 잡아야 함) | ai(지문 검토가 찾아야 함)
  script     detector가 script일 때 돌릴 스크립트 (validate, make_outputs, verdicts, stress, gen_tests, mutate)
  args       스크립트에 더 줄 인자 (선택)
  changes    {경로: 새 내용 | null(삭제) | {"replace": [옛, 새]} | {"replaces": [[옛, 새], ...]} | {"copy": 다른 경로}}
             tests/ 아래 경로는 TC를 만든 뒤에, 나머지는 만들기 전에 적용한다
  expect     script: 출력에 들어 있어야 하는 문구 / ai: 찾아야 하는 결함 설명

출력 줄(고정 문구):
  정상 문제 통과: <문제> <스크립트>
  오탐: <문제> <스크립트> — <마지막 출력 줄>
  잡음: <케이스>
  놓침: <케이스> — 기대 '<문구>'
  AI 평가 필요: <케이스> — <expect>
  결과: 스크립트 케이스 <k>/<n> 잡음, 오탐 <f>개, AI 케이스 <m>개
종료 코드: 놓침·오탐이 없으면 0
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EVAL = Path(__file__).resolve().parent
SCRIPTS = EVAL.parent / "scripts"


def script(name, problem, *args):
    r = subprocess.run([sys.executable, str(SCRIPTS / f"{name}.py"), str(problem), *args],
                       capture_output=True, text=True)
    return r.returncode, r.stdout


def apply(problem: Path, changes: dict, tests_stage: bool):
    for path, change in changes.items():
        if path.startswith("tests/") != tests_stage:
            continue
        f = problem / path
        if change is None:
            f.unlink()
        elif isinstance(change, str):
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(change, encoding="utf-8")
        elif "copy" in change:
            shutil.copy(problem / change["copy"], f)
        else:
            text = f.read_text(encoding="utf-8")
            for old, new in change.get("replaces") or [change["replace"]]:
                if text.count(old) != 1:
                    raise ValueError(f"{path}에서 바꿀 문자열을 정확히 한 번 찾지 못함: {old!r}")
                text = text.replace(old, new)
            f.write_text(text, encoding="utf-8")


def prepare(base: str, changes: dict, tmp: Path) -> Path:
    problem = tmp / base
    shutil.copytree(EVAL / "base" / base, problem,
                    ignore=shutil.ignore_patterns("tests", ".build"))
    (problem / "tests").mkdir()
    apply(problem, changes, tests_stage=False)
    script("gen_tests", problem)
    script("make_outputs", problem)
    apply(problem, changes, tests_stage=True)
    return problem


def main():
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    skip_base = "--skip-base" in sys.argv
    bases = json.loads((EVAL / "base.json").read_text(encoding="utf-8"))
    false_pos = caught = total = ai = 0

    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        if not skip_base and not names:
            for base, conf in bases.items():
                problem = prepare(base, {}, tmp / "base")
                for name, args in (("check_package", []), ("validate", []), ("make_outputs", []),
                                   ("stress", conf["stress"]), ("verdicts", []),
                                   ("mutate", conf["stress"])):
                    code, out = script(name, problem, *args)
                    if code == 0:
                        print(f"정상 문제 통과: {base} {name}")
                    else:
                        last = out.strip().splitlines()[-1] if out.strip() else ""
                        print(f"오탐: {base} {name} — {last}")
                        false_pos += 1

        for f in sorted((EVAL / "cases").glob("*.json")):
            if names and f.stem not in names:
                continue
            case = json.loads(f.read_text(encoding="utf-8"))
            if case["detector"] == "ai":
                print(f"AI 평가 필요: {f.stem} — {case['expect']}")
                ai += 1
                continue
            total += 1
            problem = prepare(case["base"], case.get("changes", {}), tmp / f.stem)
            code, out = script(case["script"], problem, *case.get("args", []))
            if code != 0 and case["expect"] in out:
                print(f"잡음: {f.stem}")
                caught += 1
            else:
                print(f"놓침: {f.stem} — 기대 '{case['expect']}'")

    print(f"결과: 스크립트 케이스 {caught}/{total} 잡음, 오탐 {false_pos}개, AI 케이스 {ai}개")
    sys.exit(0 if caught == total and not false_pos else 1)


if __name__ == "__main__":
    main()
