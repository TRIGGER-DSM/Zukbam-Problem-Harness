"""스크립트들이 같이 쓰는 컴파일·실행·비교 함수. 직접 실행하지 않는다."""
import json
import resource
import subprocess
import sys
from pathlib import Path

OK, WA, TLE, RTE = "통과", "오답", "시간 초과", "런타임 에러"
CHECKER_WA = 43  # checker 종료 코드: 0 정답, 43 오답, 그 밖은 checker 오류


def load_meta(root: Path):
    return json.loads((root / "meta.json").read_text(encoding="utf-8"))


def normalize(data: bytes):
    lines = [line.rstrip() for line in data.decode("utf-8", "replace").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def tc_key(path: Path):
    return (0, int(path.stem), "") if path.stem.isdigit() else (1, 0, path.stem)


def list_cases(root: Path, sets=("examples", "tests")):
    return [f for d in sets for f in sorted((root / d).glob("*.in"), key=tc_key)]


def rel(root: Path, path: Path):
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def compile_solution(root: Path, sol: Path):
    """실행 명령을 돌려준다. 컴파일 실패면 None."""
    if sol.suffix == ".py":
        return [sys.executable, str(sol)]
    if sol.suffix == ".cpp":
        out = root / ".build" / rel(root, sol).replace("/", "__").removesuffix(".cpp")
        out.parent.mkdir(exist_ok=True)
        if out.exists() and out.stat().st_mtime >= sol.stat().st_mtime:
            return [str(out)]
        r = subprocess.run(
            ["g++", "-O2", "-std=gnu++17", "-o", str(out), str(sol)],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            sys.stderr.write(r.stderr)
            return None
        return [str(out)]
    raise ValueError(f"지원하지 않는 풀이 형식: {sol}")


def _limit_memory(memory_mb):
    def apply():
        size = memory_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (size, size))
        _, hard = resource.getrlimit(resource.RLIMIT_STACK)
        stack = size if hard == resource.RLIM_INFINITY else min(size, hard)
        resource.setrlimit(resource.RLIMIT_STACK, (stack, hard))
    return apply


def _cpu_time():
    u = resource.getrusage(resource.RUSAGE_CHILDREN)
    return u.ru_utime + u.ru_stime


def execute(cmd, inp: Path, cap_sec, memory_mb):
    """cap_sec까지 실행한다. (상태, CPU 시간, stdout, 종료 코드). 상태는 OK·TLE·RTE.

    cap_sec을 넘으면 시간은 cap_sec으로 둔다.
    """
    before = _cpu_time()
    try:
        r = subprocess.run(
            cmd, stdin=inp.open("rb"), capture_output=True,
            timeout=cap_sec * 2 + 1, preexec_fn=_limit_memory(memory_mb),
        )
    except subprocess.TimeoutExpired:
        return TLE, cap_sec, b"", None
    used = _cpu_time() - before
    if used > cap_sec:
        return TLE, cap_sec, b"", None
    if r.returncode != 0:
        return RTE, used, r.stdout, r.returncode
    return OK, used, r.stdout, 0


def is_correct(root: Path, inp: Path, output: bytes, ans: Path):
    checker = root / "checker.py"
    if not checker.is_file():
        return normalize(output) == normalize(ans.read_bytes())
    out_file = root / ".build" / "last.out"
    out_file.parent.mkdir(exist_ok=True)
    out_file.write_bytes(output)
    code = subprocess.run(
        [sys.executable, str(checker), str(inp), str(out_file), str(ans)],
        capture_output=True,
    ).returncode
    if code not in (0, CHECKER_WA):
        sys.stderr.write(f"checker 오류: {inp.parent.name}/{inp.name} (종료 코드 {code})\n")
    return code == 0


def judge(root: Path, cmd, inp: Path, tl_sec, memory_mb, cap_sec=None):
    """TC 하나를 채점한다. (판정, CPU 시간, 종료 코드).

    cap_sec을 주면 TL보다 오래 돌려서 시간을 잰다. 판정은 항상 tl_sec 기준이다.
    """
    status, used, out, code = execute(cmd, inp, max(tl_sec, cap_sec or 0), memory_mb)
    if status == TLE or used > tl_sec:
        return TLE, used, code
    if status == RTE:
        return RTE, used, code
    return (OK if is_correct(root, inp, out, inp.with_suffix(".out")) else WA), used, code
