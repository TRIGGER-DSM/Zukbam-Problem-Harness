"""validator용 엄격한 입력 읽기 라이브러리 (testlib의 validator 부분을 Python으로 옮긴 것).

문제의 validator.py에서 이렇게 쓴다:

    import sys; sys.path.insert(0, "<harness>/scripts")  # 또는 PYTHONPATH
    from vlib import Reader
    r = Reader()
    n = r.read_int(1, 200_000, "N"); r.read_eoln()
    a = r.read_ints(n, -10**9, 10**9, "a_i"); r.read_eoln()
    r.ensure(len(set(a)) == n, "a_i가 서로 다르지 않음")
    r.finish()

공백 하나, 줄바꿈 하나까지 정확해야 통과한다. 선행 0, "-0", CR 문자, 파일 끝의 여분은 거부한다.
통과하면 변수별 관측 범위를 `범위: <변수> <최소> <최대>`로 출력하고 종료 코드 0.
실패하면 `제약 위반: <설명> (줄 <n>)`을 출력하고 종료 코드 43.
그 밖의 종료 코드(예외로 죽으면 1)는 validator 자체의 오류로 본다.
"""
import re
import sys

REJECT = 43
_INT = re.compile(rb"-?(0|[1-9][0-9]*)")


class Reader:
    def __init__(self, data: bytes = None):
        self.data = sys.stdin.buffer.read() if data is None else data
        self.pos = 0
        self.line = 1
        self.ranges = {}

    def fail(self, msg):
        print(f"제약 위반: {msg} (줄 {self.line})")
        sys.exit(REJECT)

    def ensure(self, cond, msg):
        if not cond:
            self.fail(msg)

    def _token(self, name):
        start = self.pos
        while self.pos < len(self.data) and self.data[self.pos] not in b" \n\r\t":
            self.pos += 1
        if start == self.pos:
            self.fail(f"{name}이(가) 와야 하는데 공백·줄바꿈·파일 끝이 옴")
        return self.data[start:self.pos]

    def _track(self, name, v):
        lo, hi = self.ranges.get(name, (v, v))
        self.ranges[name] = (min(lo, v), max(hi, v))

    def read_int(self, lo, hi, name):
        tok = self._token(name)
        if not _INT.fullmatch(tok) or tok == b"-0":
            self.fail(f"{name}이(가) 정수 형식이 아님: {tok[:20]!r}")
        v = int(tok)
        if not lo <= v <= hi:
            self.fail(f"{name}={v}가 범위 [{lo}, {hi}] 밖")
        self._track(name, v)
        return v

    def read_ints(self, count, lo, hi, name):
        """공백 하나로 구분된 정수 count개 (줄바꿈은 읽지 않는다)."""
        out = []
        for i in range(count):
            if i:
                self.read_space()
            out.append(self.read_int(lo, hi, name))
        return out

    def read_token(self, pattern, name):
        """정규식 pattern에 맞는 토큰 하나."""
        tok = self._token(name)
        if not re.fullmatch(pattern.encode(), tok):
            self.fail(f"{name}이(가) 형식 {pattern}에 맞지 않음: {tok[:20]!r}")
        return tok.decode()

    def _expect(self, ch: bytes, what):
        if self.data[self.pos:self.pos + 1] != ch:
            got = self.data[self.pos:self.pos + 1] or b"EOF"
            self.fail(f"{what}이(가) 와야 하는데 {got!r}이(가) 옴")
        self.pos += 1

    def read_space(self):
        self._expect(b" ", "공백 하나")

    def read_eoln(self):
        self._expect(b"\n", "줄바꿈")
        self.line += 1

    def finish(self):
        if self.pos != len(self.data):
            self.fail("입력이 끝나야 하는데 내용이 더 있음")
        for name in sorted(self.ranges):
            lo, hi = self.ranges[name]
            print(f"범위: {name} {lo} {hi}")
        sys.exit(0)
