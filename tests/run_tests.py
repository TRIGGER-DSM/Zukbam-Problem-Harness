#!/usr/bin/env python3
"""harness 스크립트 회귀 테스트. 실행: python3 tests/run_tests.py"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUN = ROOT / "scripts" / "run.py"
CHECK = ROOT / "scripts" / "check_package.py"

META = {
    "title": "A+B",
    "method": "구현",
    "keywords": ["덧셈"],
    "difficulty": "브론즈 5",
    "time_limit_ms": 300,
    "memory_mb": 256,
    "mode": 2,
}

SOLUTIONS = {
    "ok.cpp": '#include <cstdio>\nint main(){long long a,b;scanf("%lld %lld",&a,&b);printf("%lld\\n",a+b);}\n',
    "ok.py": "a, b = map(int, input().split())\nprint(a + b)\n",
    "spaces.py": "a, b = map(int, input().split())\nprint(str(a + b) + '   ')\nprint()\nprint()\n",
    "wrong.cpp": '#include <cstdio>\nint main(){long long a,b;scanf("%lld %lld",&a,&b);printf("%lld\\n",a-b);}\n',
    "tle.cpp": "int main(){volatile long long x=0;for(;;)x++;}\n",
    "rte.cpp": "#include <cstdlib>\nint main(){abort();}\n",
    "ce.cpp": "int main(){ this is not c++ }\n",
}


def make_problem(base: Path, meta=META) -> Path:
    p = base / "aplusb"
    shutil.copytree(ROOT / "templates" / "problem", p)
    (p / "meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    (p / "examples" / "1.in").write_text("1 2\n")
    (p / "examples" / "1.out").write_text("3\n")
    (p / "tests" / "1.in").write_text("1000000000 1000000000\n")
    (p / "tests" / "1.out").write_text("2000000000\n")
    for name, code in SOLUTIONS.items():
        (p / "sol" / name).write_text(code)
    return p


def run(*args):
    r = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)
    return r.returncode, r.stdout


class RunTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.p = make_problem(Path(cls.tmp.name))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def judge(self, sol):
        return run(RUN, self.p, self.p / "sol" / sol)

    def test_correct_cpp(self):
        code, out = self.judge("ok.cpp")
        self.assertEqual(code, 0, out)
        self.assertIn("통과: examples/1.in", out)
        self.assertIn("통과: tests/1.in", out)
        self.assertIn("결과: 통과 2/2", out)

    def test_correct_python(self):
        code, out = self.judge("ok.py")
        self.assertEqual(code, 0, out)
        self.assertIn("결과: 통과 2/2", out)

    def test_trailing_whitespace_ignored(self):
        code, out = self.judge("spaces.py")
        self.assertEqual(code, 0, out)

    def test_wrong_answer(self):
        code, out = self.judge("wrong.cpp")
        self.assertEqual(code, 1)
        self.assertIn("오답: examples/1.in", out)
        self.assertIn("결과: 통과 0/2", out)

    def test_time_limit(self):
        code, out = self.judge("tle.cpp")
        self.assertEqual(code, 1)
        self.assertIn("시간 초과: examples/1.in", out)

    def test_runtime_error(self):
        code, out = self.judge("rte.cpp")
        self.assertEqual(code, 1)
        self.assertIn("런타임 에러: examples/1.in", out)

    def test_compile_error(self):
        code, out = self.judge("ce.cpp")
        self.assertEqual(code, 1)
        self.assertIn("컴파일 에러: sol/ce.cpp", out)

    def test_only_one_set(self):
        code, out = run(RUN, self.p, self.p / "sol" / "ok.cpp", "--set", "examples")
        self.assertEqual(code, 0, out)
        self.assertIn("결과: 통과 1/1", out)

    def test_checker_used_when_present(self):
        with tempfile.TemporaryDirectory() as d:
            p = make_problem(Path(d))
            # 어떤 출력이든 정답으로 보는 checker
            (p / "checker.py").write_text("import sys\nsys.exit(0)\n")
            code, out = run(RUN, p, p / "sol" / "wrong.cpp")
            self.assertEqual(code, 0, out)


class CheckPackageTest(unittest.TestCase):
    def test_valid(self):
        with tempfile.TemporaryDirectory() as d:
            p = make_problem(Path(d))
            code, out = run(CHECK, p)
            self.assertEqual(code, 0, out)
            self.assertIn("패키지: 정상", out)

    def test_template_meta_is_incomplete(self):
        # 템플릿 그대로는 통과하면 안 된다 (빈 값 채우기를 잊은 경우)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x"
            shutil.copytree(ROOT / "templates" / "problem", p)
            code, out = run(CHECK, p)
            self.assertEqual(code, 1, out)

    def test_missing_field(self):
        with tempfile.TemporaryDirectory() as d:
            meta = dict(META)
            del meta["time_limit_ms"]
            p = make_problem(Path(d), meta)
            code, out = run(CHECK, p)
            self.assertEqual(code, 1)
            self.assertIn("meta.json 문제: time_limit_ms", out)

    def test_unpaired_tc(self):
        with tempfile.TemporaryDirectory() as d:
            p = make_problem(Path(d))
            (p / "tests" / "2.in").write_text("1 1\n")
            code, out = run(CHECK, p)
            self.assertEqual(code, 1)
            self.assertIn("짝 없음: tests/2.in", out)



# ---- testgen / testcheck 스크립트 ----

VALIDATOR = """from vlib import Reader
r = Reader()
r.read_int(-10**9, 10**9, "a")
r.read_space()
r.read_int(-10**9, 10**9, "b")
r.read_eoln()
r.finish()
"""
LENIENT_VALIDATOR = "import sys\na, b = map(int, sys.stdin.read().split())\n"
GEN = """import random, sys
rnd = random.Random(sys.argv[1] + sys.argv[2])
m = int(sys.argv[1])
print(rnd.randint(-m, m), rnd.randint(-m, m))
"""
BRUTE = '#include <cstdio>\nint main(){long long a,b;scanf("%lld %lld",&a,&b);long long s=a;for(long long i=0;i<(b<0?-b:b);i++)s+=(b<0?-1:1);printf("%lld\\n",s);}\n'


def make_full(base: Path) -> Path:
    p = make_problem(base)
    for name in list(SOLUTIONS):
        (p / "sol" / name).unlink()
    (p / "sol" / "main.cpp").write_text(SOLUTIONS["ok.cpp"])
    (p / "sol" / "main.py").write_text(SOLUTIONS["ok.py"])
    (p / "sol" / "brute.cpp").write_text(BRUTE)
    (p / "sol" / "wrong_answer" / "minus.cpp").write_text(SOLUTIONS["wrong.cpp"])
    (p / "sol" / "time_limit_exceeded" / "loop.cpp").write_text(SOLUTIONS["tle.cpp"])
    (p / "sol" / "runtime_error" / "abort.cpp").write_text(SOLUTIONS["rte.cpp"])
    (p / "validator.py").write_text(VALIDATOR)
    (p / "gen" / "gen.py").write_text(GEN)
    (p / "gen" / "tests.txt").write_text("# 작은 값\n5 1\n1000000000 1\n")
    (p / "invalid" / "too-large.in").write_text("1000000001 1\n")
    return p


SCRIPT = {n: ROOT / "scripts" / f"{n}.py" for n in
          ("validate", "gen_tests", "make_outputs", "stress", "verdicts")}


class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.p = make_full(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    # validate
    def test_validate_ok(self):
        code, out = run(SCRIPT["validate"], self.p)
        self.assertEqual(code, 0, out)
        self.assertIn("범위: a 1 1000000000", out)

    def test_validate_lenient_validator(self):
        (self.p / "validator.py").write_text(LENIENT_VALIDATOR)
        code, out = run(SCRIPT["validate"], self.p)
        self.assertEqual(code, 1)
        self.assertIn("거부 안 함: 줄 끝 공백 (examples/1.in)", out)
        self.assertIn("거부 안 함: 선행 0 (examples/1.in)", out)
        self.assertIn("거부 안 함: invalid/too-large.in", out)

    def test_validate_crash_is_not_rejection(self):
        # 행 길이를 안 보고 인덱스로 접근하다 죽는 validator: 거부가 아니라 오류
        (self.p / "validator.py").write_text(
            "import sys\na, b = sys.stdin.read().split(' ')\nint(a); int(b)\n")
        code, out = run(SCRIPT["validate"], self.p)
        self.assertEqual(code, 1)
        self.assertIn("validator 오류: 공백 두 칸 (examples/1.in) (종료 코드 1)", out)

    def test_validate_rejects_bad_tc(self):
        (self.p / "tests" / "2.in").write_text("1 2 \n")
        (self.p / "tests" / "2.out").write_text("3\n")
        code, out = run(SCRIPT["validate"], self.p)
        self.assertEqual(code, 1)
        self.assertIn("validator 거부: tests/2.in", out)
        self.assertIn("형식 문제: tests/2.in 줄 끝 공백 (줄 1)", out)

    def test_validate_duplicate(self):
        (self.p / "tests" / "2.in").write_text("1 2\n")
        (self.p / "tests" / "2.out").write_text("3\n")
        code, out = run(SCRIPT["validate"], self.p)
        self.assertIn("중복 입력: tests/2.in = examples/1.in", out)

    def test_validate_checker_crash(self):
        (self.p / "checker.py").write_text("import sys\nint(open(sys.argv[2]).read())\n")
        code, out = run(SCRIPT["validate"], self.p)
        self.assertEqual(code, 1)
        self.assertIn("checker 오류: 출력 b'' (종료 코드 1)", out)

    # gen_tests
    def test_gen_tests(self):
        code, out = run(SCRIPT["gen_tests"], self.p, "--start", "2")
        self.assertEqual(code, 0, out)
        self.assertIn("생성: tests/2.in (5 1)", out)
        self.assertTrue((self.p / "tests" / "3.in").is_file())

    def test_gen_tests_removes_stale_out(self):
        run(SCRIPT["gen_tests"], self.p, "--start", "2")
        run(SCRIPT["make_outputs"], self.p)
        (self.p / "gen" / "tests.txt").write_text("7 1\n1000000000 1\n")
        code, out = run(SCRIPT["gen_tests"], self.p, "--start", "2")
        self.assertIn("이전 출력 삭제: tests/2.out", out)
        self.assertNotIn("이전 출력 삭제: tests/3.out", out)  # 3번 입력은 그대로
        self.assertFalse((self.p / "tests" / "2.out").exists())

    def test_gen_tests_nondeterministic(self):
        (self.p / "gen" / "gen.py").write_text("import time\nprint(time.time_ns() % 1000, 1)\n")
        code, out = run(SCRIPT["gen_tests"], self.p)
        self.assertEqual(code, 1)
        self.assertIn("비결정적: 줄 2", out)

    # make_outputs
    def test_make_outputs(self):
        run(SCRIPT["gen_tests"], self.p, "--start", "2")
        code, out = run(SCRIPT["make_outputs"], self.p)
        self.assertEqual(code, 0, out)
        self.assertIn("작성: tests/2.out", out)
        self.assertIn("결과: 작성 2, 일치 2", out)

    def test_make_outputs_user_out_differs(self):
        (self.p / "tests" / "1.out").write_text("1\n")
        code, out = run(SCRIPT["make_outputs"], self.p)
        self.assertEqual(code, 1)
        self.assertIn("정답과 다름: tests/1.in", out)

    def test_make_outputs_example_out_only_in_mode1(self):
        (self.p / "examples" / "2.in").write_text("4 5\n")
        code, out = run(SCRIPT["make_outputs"], self.p)
        self.assertEqual(code, 1)
        self.assertIn("예제 출력 없음: examples/2.in", out)
        meta = json.loads((self.p / "meta.json").read_text())
        meta["mode"] = 1  # AI가 만든 문제는 예제 출력도 정답으로 만든다
        (self.p / "meta.json").write_text(json.dumps(meta))
        code, out = run(SCRIPT["make_outputs"], self.p)
        self.assertEqual(code, 0, out)
        self.assertIn("작성: examples/2.out", out)
        self.assertEqual((self.p / "examples" / "2.out").read_text(), "9\n")

    # stress
    def test_stress_agree(self):
        code, out = run(SCRIPT["stress"], self.p, "--gen", "5 {seed}", "--count", "20")
        self.assertEqual(code, 0, out)
        self.assertIn("결과: 일치 20/20", out)

    def test_stress_mismatch(self):
        code, out = run(SCRIPT["stress"], self.p, "--gen", "5 {seed}", "--count", "20",
                        "--a", "sol/wrong_answer/minus.cpp")
        self.assertEqual(code, 1)
        self.assertIn("불일치:", out)
        self.assertTrue((self.p / ".build" / "stress" / "smallest.in").is_file())

    def test_stress_invalid_generated_input(self):
        code, out = run(SCRIPT["stress"], self.p, "--gen", "2000000000 {seed}", "--count", "3")
        self.assertEqual(code, 1)
        self.assertIn("생성 입력 제약 위반: 2000000000 {seed} seed 1", out)

    # verdicts
    def test_verdicts_ok(self):
        code, out = run(SCRIPT["verdicts"], self.p)
        self.assertEqual(code, 0, out)
        self.assertIn("시간 제한 조건 만족", out)
        self.assertIn("판정: 정상", out)

    def test_verdicts_unset_time_limit(self):
        meta = json.loads((self.p / "meta.json").read_text())
        meta["time_limit_ms"] = 0
        (self.p / "meta.json").write_text(json.dumps(meta))
        code, out = run(SCRIPT["verdicts"], self.p)
        self.assertIn("시간 제한 미정: 1000ms 기준으로 측정", out)
        self.assertIn("추천 시간 제한: 500ms", out)
        self.assertIn("풀이: sol/main.cpp — 통과 2", out)

    def test_verdicts_wrong_in_accepted(self):
        (self.p / "sol" / "accepted" / "bad.cpp").write_text(SOLUTIONS["wrong.cpp"])
        code, out = run(SCRIPT["verdicts"], self.p)
        self.assertEqual(code, 1)
        self.assertIn("기대와 다름: sol/accepted/bad.cpp — 허용되지 않는 판정 오답", out)

    def test_verdicts_weak_tests(self):
        # 오답 풀이가 통과해버리면 TC가 약한 것
        (self.p / "sol" / "wrong_answer" / "fake.cpp").write_text(SOLUTIONS["ok.cpp"])
        code, out = run(SCRIPT["verdicts"], self.p)
        self.assertEqual(code, 1)
        self.assertIn("기대와 다름: sol/wrong_answer/fake.cpp — 오답이(가) 한 번도 안 나옴", out)

    def test_verdicts_tle_solution_too_fast(self):
        (self.p / "sol" / "time_limit_exceeded" / "loop.cpp").write_text(SOLUTIONS["ok.cpp"])
        code, out = run(SCRIPT["verdicts"], self.p)
        self.assertEqual(code, 1)
        self.assertIn("기대와 다름: sol/time_limit_exceeded/loop.cpp — 시간 초과이(가) 한 번도 안 나옴", out)

    # mutate
    def test_mutate_finds_hole(self):
        # TC가 양수뿐이라 scanf를 %d로 잘못 읽는 변이가 통과한다. 작은 랜덤 입력(음수 포함)에서 드러난다
        code, out = run(ROOT / "scripts" / "mutate.py", self.p, "--gen", "5 {seed}", "--count", "20")
        self.assertEqual(code, 1, out)
        self.assertIn("TC 구멍: L2:33 '%lld'→'%d'", out)
        self.assertTrue((self.p / ".build" / "mutate" / "hole-1.cpp").is_file())

    def test_mutate_no_hole(self):
        (self.p / "tests" / "2.in").write_text("-3 -4\n")
        (self.p / "tests" / "2.out").write_text("-7\n")
        code, out = run(ROOT / "scripts" / "mutate.py", self.p, "--gen", "5 {seed}", "--count", "20")
        self.assertEqual(code, 0, out)
        self.assertIn("결과: TC 구멍 0개", out)
        # 출력은 2e9까지라 printf의 %d도 결과가 같다
        self.assertIn("동등 추정: L2:59 '%lld'→'%d'", out)



# ---- 시작 메뉴 ----

class WelcomeTest(unittest.TestCase):
    def welcome(self, root):
        # welcome.py는 자기 위치 기준으로 problems/를 보므로 harness 사본에서 돌린다
        shutil.copytree(ROOT / "scripts", root / "scripts")
        r = subprocess.run([sys.executable, str(root / "scripts" / "welcome.py")], capture_output=True, text=True)
        return json.loads(r.stdout)

    def test_menu(self):
        with tempfile.TemporaryDirectory() as d:
            out = self.welcome(Path(d))
            self.assertIn("1. 새 문제 만들기", out["systemMessage"])
            self.assertIn("[토큰 안내]", out["systemMessage"])
            self.assertIn("4. 가지고 있는 테스트케이스 검증", out["systemMessage"])
            self.assertNotIn("이어서 하기", out["systemMessage"])
            self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "SessionStart")

    def test_menu_lists_unfinished(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for name, stage in (("a", "reviewed"), ("b", "done")):
                (root / "problems" / name).mkdir(parents=True)
                (root / "problems" / name / "state.md").write_text(f"stage: {stage}\nmode: 2\n")
            out = self.welcome(root)
            self.assertIn("5. 이어서 하기", out["systemMessage"])
            self.assertIn("- a (단계: reviewed)", out["systemMessage"])
            self.assertNotIn("- b", out["systemMessage"])

    def test_menu_asks_model_first_time(self):
        with tempfile.TemporaryDirectory() as d:
            out = self.welcome(Path(d))
            self.assertIn("처음 쓰시는군요!", out["systemMessage"])
            self.assertIn("0절(모델 정하기)", out["hookSpecificOutput"]["additionalContext"])

    def test_menu_shows_model_config(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "harness.local.json").write_text('{"main_model": "sonnet", "helper_model": "haiku"}')
            out = self.welcome(root)
            self.assertNotIn("처음 쓰시는군요!", out["systemMessage"])
            self.assertIn("모델: 메인 sonnet, 보조 에이전트 haiku", out["systemMessage"])


# ---- 참고 문제 조회 ----

REFS_DATA = {
    "fetched": "2026-10-13",
    "tags": {"dp": {"ko": "다이나믹 프로그래밍", "aliases": ["동적계획법"]},
             "prefix_sum": {"ko": "누적 합", "aliases": ["구간합"]}},
    "problems": [
        {"id": 1, "title": "가", "level": 13, "solved": 50, "tags": ["dp", "prefix_sum"]},
        {"id": 2, "title": "나", "level": 13, "solved": 40, "tags": ["dp"]},
        {"id": 3, "title": "다", "level": 13, "solved": 30, "tags": ["prefix_sum"]},
        {"id": 4, "title": "라", "level": 8, "solved": 90, "tags": ["dp"]},
    ],
}


class RefsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.data = Path(cls.tmp.name) / "refs.json"
        cls.data.write_text(json.dumps(REFS_DATA, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def refs(self, *args):
        return run(ROOT / "scripts" / "refs.py", *args, "--data", self.data)

    def test_query(self):
        code, out = self.refs("동적 계획법", "골드 3")
        self.assertEqual(code, 0, out)
        self.assertIn("태그: dp (다이나믹 프로그래밍)", out)
        self.assertIn("티어: 골드 3", out)
        self.assertIn("표본: 이 티어 3문제 중 2문제", out)
        self.assertIn("함께 붙는 태그: 누적 합 1", out)
        self.assertIn("대표 문제: 1 가 [다이나믹 프로그래밍, 누적 합] (푼 사람 50)", out)
        self.assertIn("티어별 분포: 실버 3 1, 골드 3 2", out)

    def test_tier_formats(self):
        for tier in ("g3", "G3", "골드3"):
            self.assertIn("티어: 골드 3", self.refs("dp", tier)[1])

    def test_not_found(self):
        code, out = self.refs("xyz", "g3")
        self.assertEqual(code, 1)
        self.assertIn("태그를 찾지 못함: xyz", out)
        code, out = self.refs("dp", "금3")
        self.assertIn("티어를 읽지 못함: 금3", out)
        code, out = self.refs("누적합", "s3")  # 이 티어 표본에 없음
        self.assertEqual(code, 1)
        self.assertIn("표본: 이 티어 1문제 중 0문제", out)


# ---- 서브에이전트 파일 접근 훅 ----

GUARD = ROOT / "scripts" / "agent_guard.py"
BLIND = "test-problem-maker-blind-solver"
VWRITER = "test-problem-maker-validator-writer"
WSOLVER = "test-problem-maker-wrong-solver"
FSOLVER = "test-problem-maker-fast-solver"


def guard(agent, tool, tool_input, cwd):
    payload = {"tool_name": tool, "tool_input": tool_input, "cwd": str(cwd)}
    if agent:
        payload["agent_type"] = agent
    r = subprocess.run([sys.executable, str(GUARD)], input=json.dumps(payload),
                       capture_output=True, text=True)
    return r.returncode


class GuardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.p = make_full(Path(cls.tmp.name))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def read(self, agent, rel):
        return guard(agent, "Read", {"file_path": str(self.p / rel)}, ROOT)

    def test_main_thread_untouched(self):
        self.assertEqual(self.read(None, "sol/main.cpp"), 0)

    def test_blind_reads(self):
        self.assertEqual(self.read(BLIND, "problem.md"), 0)
        self.assertEqual(self.read(BLIND, "examples/1.in"), 0)
        for rel in ("sol/main.cpp", "sol/main.py", "tests/1.in", "gen/gen.py", "validator.py",
                    "sol/wrong_answer/minus.cpp", "report.md"):
            self.assertEqual(self.read(BLIND, rel), 2, rel)

    def test_blind_cannot_read_eval_answers(self):
        f = ROOT / "eval" / "base" / "ant-food-sum" / "sol" / "main.cpp"
        self.assertEqual(guard(BLIND, "Read", {"file_path": str(f)}, ROOT), 2)
        self.assertEqual(guard(BLIND, "Read", {"file_path": str(ROOT / "rules" / "principles.md")}, ROOT), 2)

    def test_blind_writes(self):
        w = lambda rel: guard(BLIND, "Write", {"file_path": str(self.p / rel), "content": ""}, ROOT)
        self.assertEqual(w("sol/brute.cpp"), 0)
        self.assertEqual(w("sol/blind-2.cpp"), 0)
        self.assertEqual(w("sol/main.cpp"), 2)
        self.assertEqual(w("tests/1.out"), 2)
        self.assertEqual(guard(BLIND, "Write", {"file_path": "/tmp/x.cpp"}, ROOT), 0)

    def test_blind_bash(self):
        b = lambda cmd: guard(BLIND, "Bash", {"command": cmd}, self.p)
        self.assertEqual(b("g++ -O2 -o /tmp/brute sol/brute.cpp && /tmp/brute < examples/1.in"), 0)
        self.assertEqual(b("cat sol/main.cpp"), 2)
        self.assertEqual(b("cat tests/1.in"), 2)
        self.assertEqual(b("find . -name '*.cpp'"), 2)
        self.assertEqual(b("grep -rn pre ."), 2)
        self.assertEqual(b("ls -R"), 2)
        self.assertEqual(b("git log"), 2)
        # 저장소 경로에 'git'이 들어 있어도 허용된 명령은 막지 않는다
        self.assertEqual(b(f"g++ -O2 -o /tmp/b {self.p}/sol/brute.cpp && /tmp/b < /home/u/coding/git/x/examples/1.in"), 0)
        self.assertEqual(b(f"cat /home/u/coding/git/x/sol/main.cpp"), 2)

    def test_validator_writer(self):
        self.assertEqual(self.read(VWRITER, "problem.md"), 0)
        self.assertEqual(guard(VWRITER, "Read", {"file_path": str(ROOT / "scripts" / "vlib.py")}, ROOT), 0)
        self.assertEqual(guard(VWRITER, "Read", {"file_path": str(ROOT / "rules" / "package.md")}, ROOT), 0)
        self.assertEqual(self.read(VWRITER, "gen/gen.py"), 2)
        self.assertEqual(self.read(VWRITER, "sol/main.cpp"), 2)
        w = lambda rel: guard(VWRITER, "Write", {"file_path": str(self.p / rel)}, ROOT)
        self.assertEqual(w("validator.py"), 0)
        self.assertEqual(w("invalid/n-too-large.in"), 0)
        self.assertEqual(w("gen/gen.py"), 2)
        b = lambda cmd: guard(VWRITER, "Bash", {"command": cmd}, ROOT)
        self.assertEqual(b(f"python3 scripts/validate.py {self.p}"), 0)
        self.assertEqual(b(f"cat {self.p}/gen/gen.py"), 2)

    def test_wrong_solver(self):
        self.assertEqual(self.read(WSOLVER, "problem.md"), 0)
        self.assertEqual(self.read(WSOLVER, "sol/wrong_answer/minus.cpp"), 0)
        for rel in ("sol/main.cpp", "sol/brute.cpp", "tests/1.in", "gen/gen.py", "validator.py"):
            self.assertEqual(self.read(WSOLVER, rel), 2, rel)
        w = lambda rel: guard(WSOLVER, "Write", {"file_path": str(self.p / rel)}, ROOT)
        self.assertEqual(w("sol/wrong_answer/off-by-one.cpp"), 0)
        self.assertEqual(w("sol/time_limit_exceeded/slow.cpp"), 0)
        self.assertEqual(w("sol/main.cpp"), 2)
        self.assertEqual(w("sol/accepted/x.cpp"), 2)
        b = lambda cmd: guard(WSOLVER, "Bash", {"command": cmd}, self.p)
        self.assertEqual(b("g++ -O2 -o /tmp/w sol/wrong_answer/minus.cpp && /tmp/w < examples/1.in"), 0)
        self.assertEqual(b("cat sol/main.cpp"), 2)
        self.assertEqual(b("cat tests/1.in"), 2)

    def test_fast_solver(self):
        self.assertEqual(self.read(FSOLVER, "problem.md"), 0)
        for rel in ("sol/main.cpp", "sol/brute.cpp", "sol/wrong_answer/minus.cpp", "tests/1.in"):
            self.assertEqual(self.read(FSOLVER, rel), 2, rel)
        w = lambda rel: guard(FSOLVER, "Write", {"file_path": str(self.p / rel)}, ROOT)
        self.assertEqual(w("sol/accepted/blind-fast.cpp"), 0)
        self.assertEqual(w("sol/probe-haiku.cpp"), 0)
        self.assertEqual(w("sol/accepted/other.cpp"), 2)
        self.assertEqual(w("sol/main.cpp"), 2)
        b = lambda cmd: guard(FSOLVER, "Bash", {"command": cmd}, self.p)
        self.assertEqual(b("g++ -O2 -o /tmp/f sol/probe-haiku.cpp && /tmp/f < examples/1.in"), 0)
        self.assertEqual(b("cat sol/main.cpp"), 2)

    def test_bash_cd_then_bare_name(self):
        # 실제 실행에서 wrong-solver가 `cd sol; cat README.md`로 정답 근거를 읽었다
        sol = self.p / "sol"
        self.assertEqual(guard(WSOLVER, "Bash", {"command": f"cd {sol}; ls wrong_answer; cat README.md"}, ROOT), 2)
        self.assertEqual(guard(BLIND, "Bash", {"command": f"cd {sol} && cat main.cpp"}, ROOT), 2)
        self.assertEqual(guard(FSOLVER, "Bash", {"command": f"cd {sol}/accepted && cat other.cpp"}, ROOT), 2)
        self.assertEqual(guard(WSOLVER, "Bash", {"command": "cat ../tests/1.in"}, sol), 2)
        # 슬러그에 이름이 들어 있는 것은 막지 않는다
        self.assertEqual(guard(WSOLVER, "Bash", {"command": "cd /x/problems/charger-gen/sol/wrong_answer && g++ a.cpp"}, ROOT), 0)

    def test_grep_denied(self):
        self.assertEqual(guard(BLIND, "Grep", {"pattern": "x", "path": str(self.p)}, ROOT), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
