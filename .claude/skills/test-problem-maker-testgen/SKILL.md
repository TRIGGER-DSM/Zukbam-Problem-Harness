---
name: test-problem-maker-testgen
description: 확정된 지문으로 정답·오답 풀이, 생성기, validator, 숨은 TC를 만든다. test-problem-maker-start만 호출한다.
---

# test-problem-maker-testgen

먼저 `rules/principles.md`, `rules/package.md`를 읽는다. 항목 번호(T1 등)는 `docs/research/checklist.md`의 것이다.
아래 명령은 harness 루트에서 실행하고, `P`는 문제 폴더(`problems/<슬러그>`)다.
스크립트 출력은 고치지 않고 `report.md`에 그대로 붙인다.

## 1. 정답과 풀이 근거
1. 사용자가 정답 코드를 줬으면 `sol/main.cpp`에 둔다. 없으면 직접 쓴다.
2. `sol/main.py`(Python 정답)를 쓴다. 상수 최적화 없이 평범하게 쓰되 입력은 `sys.stdin.buffer`로 한 번에 읽는다.
3. `sol/README.md`에 왜 맞는지(정당성), 복잡도를 쓴다. 증명을 쓸 수 없으면 그렇다고 적는다. 사람이 검토할 항목이다.

## 2. 독립 풀이, validator, 떨어뜨릴 풀이 (서브에이전트 네 개를 동시에)
- `test-problem-maker-blind-solver`: 문제 폴더 경로만 주고 `sol/brute.cpp`를 쓰게 한다. 정답 코드 내용을 프롬프트에 넣지 않는다.
- `test-problem-maker-validator-writer`: 문제 폴더 경로만 주고 `validator.py`와 `invalid/`를 쓰게 한다.
- `test-problem-maker-wrong-solver`: 문제 폴더 경로만 주고 `sol/wrong_answer/` 등에 떨어뜨릴 풀이를 쓰게 한다.
- `test-problem-maker-fast-solver`: 문제 폴더 경로만 주고 `sol/accepted/blind-fast.cpp`에 두 번째 정답을 쓰게 한다. 주 정답과 따로 푼 풀이가 같은 답을 내야 정답을 믿는다. "못 풂"이면 [질문]으로 보고한다 (문제가 의도보다 어렵거나 지문이 부족하다는 신호).

네 에이전트가 보고한 **해석이 갈리는 곳**, **범위가 없는 변수**, **예제 불일치**는 지문 결함이다. 직접 정하지 말고 [질문]으로 모은다.

## 3. 정답과 brute-force 대조
`gen/gen.py`를 먼저 쓴다 (5절). 그다음:
```
python3 scripts/stress.py P --gen "<작은 입력 인자 {seed}>" [--gen ...] --count 200
```
- 작은 입력이 **모든 경우**를 만들 수 있어야 한다: n을 고정하지 않고, 값이 겹치거나 같을 수 있고, 그래프가 연결되지 않을 수 있게 (T13).
- 두 번째 정답과도 대조한다. 작은 입력과 함께, brute가 못 도는 중간 크기 입력도 넣는다:
  `python3 scripts/stress.py P --gen "<작은 입력 {seed}>" --gen "<중간 크기 {seed}>" --b sol/accepted/blind-fast.cpp --count 200`
- 불일치가 나오면 가장 작은 입력을 손으로 따라가 누가 틀렸는지 판단한다 (작은 입력이면 brute가 기준). 지문 해석 차이 때문이면 [질문]. **brute나 두 번째 정답을 주 정답에 맞춰 고치지 않는다.**

## 4. 떨어뜨릴 풀이
wrong-solver가 쓴 풀이는 **6절에서 `verdicts.py`를 처음 돌리기 전까지 열어 보지 않는다.** TC를 그 풀이에 맞추지 않고 만들어야, 처음 결과가 TC의 실제 강도를 보여 준다.
에이전트 보고의 파일 이름과 한 줄 설명만 보고, 빠진 종류(T18: 오버플로 지점마다, 경우 나누기마다)가 있으면 직접 더 쓴다.

## 5. 생성기와 TC 목록
- `gen/gen.py <인자...> <seed>`: 같은 인자면 같은 출력 (`random.Random(<인자 전체를 이은 문자열>)`). 모드 이름은 의미 있게 (`small`, `max`, `touch`, ...). 맨 위 docstring에 모드별 설명.
- 조건을 만족할 때까지 다시 뽑는 while 재시도 대신 구조를 직접 만든다 (T9).
- `gen/tests.txt` 순서: 작은 경우 → 경계(최소·최대, 같은 값, 답 최대/최소) → 최대 크기 → **떨어뜨릴 풀이마다 그것을 잡는 전용 TC**(T19) → 랜덤. 줄마다 `#` 주석으로 무엇을 노리는지 적는다.

## 6. 만들고 검사하기
```
python3 scripts/gen_tests.py P [--start <사용자 TC 다음 번호>]
python3 scripts/validate.py P
python3 scripts/make_outputs.py P
python3 scripts/verdicts.py P
```
- `validate.py`: `거부 안 함`·`validator 오류`면 validator-writer에게 그 줄을 주고 고치게 한다. `validator 거부`면 생성기를 고친다.
- `verdicts.py`의 `기대와 다름`:
  - 떨어뜨릴 풀이가 통과했다 → **그 풀이를 잡는 TC를 추가**한다. 풀이를 더 틀리게 고치지 않는다. 처음 결과에서 통과한 개수를 `report.md`에 남긴다.
  - 그 풀이가 사실은 맞다(다른 정답) → `sol/accepted/`로 옮긴다.
  - 판정이 섞여 나온다(오답과 런타임 에러 등) → 정의되지 않은 동작이라 기대 판정을 정할 수 없다. 그 풀이는 지우고 `report.md`에 무엇이었는지 적는다. 다른 폴더로 옮겨 두지 않는다.
  - 정답이 실패했다 → 정답 또는 TC 문제. 3절로 돌아간다.
- 위가 모두 정상이면 변이 테스트를 돌린다 (`--gen`은 3절 stress와 같게):
  ```
  python3 scripts/mutate.py P --gen "<작은 입력 인자 {seed}>" [--gen ...]
  ```
  `TC 구멍: ... — <인자>` 마다 그 인자 줄을 `gen/tests.txt`에 `# 변이 테스트가 찾은 구멍: <설명>` 주석과 함께 더하고, 알려 준 `hole-<n>.cpp`를 `sol/wrong_answer/mutant-<설명>.cpp`로 옮긴 뒤 `gen_tests.py`부터 다시 한다. `동등 추정`은 `report.md`에 그대로 적는다.
- 시간 제한: `meta.json`의 `time_limit_ms`가 0이면 `verdicts.py`의 `추천 시간 제한`을 넣고 다시 돌린다. `추천 시간 제한: 없음`이면 입력 크기를 키워 본 뒤, 그래도 없으면 [질문].
- 같은 문제로 3번 고쳐도 해결되지 않으면 멈추고 남은 문제를 보고한다.

## 7. 끝
`sol/README.md`의 "의도적으로 떨어뜨리는 풀이" 표를 채운다. `report.md`에 위 스크립트의 마지막 출력을 붙이고, stress 대조 횟수와 불일치 여부, [질문] 목록을 적는다. `state.md`의 `stage`를 `tested`로 바꾼다.
