#!/usr/bin/env python3
"""서브에이전트의 파일 접근을 제한하는 PreToolUse 훅 (.claude/settings.json에 등록).

stdin으로 훅 입력(JSON)을 받는다. agent_type이 아래 POLICIES에 없으면(메인 대화 등) 아무것도 하지 않는다.
막을 때는 종료 코드 2와 이유(stderr)를 낸다. Claude Code가 그 이유를 에이전트에게 보여준다.

문제 폴더는 meta.json이 있는 가장 가까운 상위 폴더로 찾는다. 그 안의 경로는 허용 목록과 비교하고,
harness 폴더 안이면서 문제 폴더가 아닌 경로는 HARNESS_READ에 있을 때만 읽을 수 있다.

보안 경계가 아니다. 지침을 어기고 실수로 정답·TC를 보는 것을 막는 린트다.
Bash는 명령 문자열에 금지 경로 조각이나 넓은 탐색 명령이 있으면 막는다.
"""
import json
import os
import re
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parent.parent
WRONG_DIRS = r"sol/(wrong_answer|time_limit_exceeded|runtime_error)(/.*)?"
FAST_FILES = r"sol/(accepted/blind-fast|probe-[\w-]+)\.cpp"

# Bash는 경로가 아니라 파일·폴더 이름으로 본다. `cd sol; cat README.md`처럼 폴더에 들어간 뒤
# 이름만으로 읽는 것도 막기 위해서다 (실제 실행에서 이렇게 정답 근거를 읽은 일이 있었다).
W = r"(?<![\w-])"  # 슬러그(예: charger-gen)의 일부는 이름으로 보지 않는다
NAMES = {
    "readme": W + r"README\.md", "main": W + r"main\.(cpp|py)\b", "brute": W + r"brute\.cpp",
    "blind2": W + r"blind-2\.cpp", "fast": W + r"blind-fast\.cpp", "probe": W + r"probe-[\w-]+\.cpp",
    "accepted": W + r"accepted(?![\w-])", "wrong": W + r"(wrong_answer|time_limit_exceeded|runtime_error)(?![\w-])",
    "tests": W + r"tests(?![\w-])", "gen": W + r"gen(?![\w-])", "validator": r"validator",
    "invalid": W + r"invalid(?![\w-])", "checker": r"checker", "report": W + r"report\.md",
    "state": W + r"state\.md", "eval": W + r"eval(?![\w-])",
}


def forbid(*allowed):
    return [pattern for name, pattern in NAMES.items() if name not in allowed]


POLICIES = {
    "test-problem-maker-blind-solver": {
        "read": [r"problem\.md", r"examples(/.*)?", r"sol/brute\.cpp", r"sol/blind-2\.cpp"],
        "write": [r"sol/brute\.cpp", r"sol/blind-2\.cpp"],
        "harness_read": [],
        "bash_forbidden": forbid("brute", "blind2"),
    },
    "test-problem-maker-validator-writer": {
        "read": [r"problem\.md", r"examples(/.*)?", r"validator\.py", r"invalid(/.*)?"],
        "write": [r"validator\.py", r"invalid/.*"],
        "harness_read": [r"rules/package\.md", r"scripts/vlib\.py"],
        "bash_forbidden": forbid("validator", "invalid"),
    },
    "test-problem-maker-fast-solver": {
        "read": [r"problem\.md", r"examples(/.*)?", FAST_FILES],
        "write": [FAST_FILES],
        "harness_read": [],
        "bash_forbidden": forbid("fast", "probe", "accepted") + [W + r"accepted(?!/blind-fast\.cpp)"],
    },
    "test-problem-maker-wrong-solver": {
        "read": [r"problem\.md", r"examples(/.*)?", WRONG_DIRS],
        "write": [WRONG_DIRS],
        "harness_read": [],
        "bash_forbidden": forbid("wrong"),
    },
}
# 어느 에이전트든 Bash에서 막는 넓은 탐색
BASH_SEARCH = [r"(^|[;&|]\s*)(find|tree|rg|ag|locate)\b", r"\bgrep\b[^|;&]*\s-[a-zA-Z]*[rR]",
               r"\bls\b[^|;&]*\s-[a-zA-Z]*R", r"(^|[;&|]\s*)git\s"]
SCRATCH = [Path("/tmp")]


def deny(reason):
    sys.stderr.write(f"[agent_guard] 막음: {reason}\n")
    sys.exit(2)


def problem_root(path: Path):
    for d in [path] + list(path.parents):
        if (d / "meta.json").is_file():
            return d
    return None


def check_path(path_str, kind, policy, cwd):
    path = Path(path_str)
    if not path.is_absolute():
        path = Path(cwd) / path
    path = Path(os.path.normpath(path))
    root = problem_root(path if path.is_dir() else path.parent)
    if root is not None:
        rel = path.relative_to(root).as_posix()
        if rel == "." and kind == "read":
            return  # 문제 폴더 자체를 나열하는 것은 허용 (파일 이름만 보인다)
        if not any(re.fullmatch(p, rel) for p in policy[kind]):
            deny(f"{rel} 은(는) 이 에이전트가 {'읽을' if kind == 'read' else '쓸'} 수 없는 파일이다")
        return
    if path == HARNESS or HARNESS in path.parents:
        rel = path.relative_to(HARNESS).as_posix()
        if kind == "read" and any(re.fullmatch(p, rel) for p in policy["harness_read"]):
            return
        deny(f"harness의 {rel} 은(는) 이 에이전트가 볼 수 없다")
    if kind == "write" and not any(s == path or s in path.parents for s in SCRATCH):
        deny(f"{path} 에는 쓸 수 없다 (문제 폴더의 허용된 파일과 /tmp만)")


def main():
    data = json.load(sys.stdin)
    policy = POLICIES.get(data.get("agent_type") or "")
    if policy is None:
        sys.exit(0)
    tool = data.get("tool_name", "")
    inp = data.get("tool_input", {}) or {}
    cwd = data.get("cwd") or os.getcwd()

    if tool == "Read":
        check_path(inp.get("file_path", ""), "read", policy, cwd)
    elif tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        check_path(inp.get("file_path") or inp.get("notebook_path", ""), "write", policy, cwd)
    elif tool in ("Grep", "Glob"):
        check_path(inp.get("path") or cwd, "read", policy, cwd)
        if tool == "Grep" or "**" in inp.get("pattern", ""):
            deny("넓은 탐색(Grep, ** 패턴)은 쓸 수 없다. 필요한 파일을 이름으로 읽는다")
    elif tool == "Bash":
        cmd = inp.get("command", "")
        for pat in BASH_SEARCH + policy["bash_forbidden"]:
            if re.search(pat, cmd):
                deny(f"이 명령은 허용되지 않는 경로나 넓은 탐색을 포함한다 ({pat})")
    else:
        deny(f"{tool} 도구는 이 에이전트에게 허용되지 않는다")
    sys.exit(0)


if __name__ == "__main__":
    main()
