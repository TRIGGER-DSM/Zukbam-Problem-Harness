# Zukbam Problem Harness

학교 코딩테스트 사이트 Zukbam에 올릴 백준식(stdin/stdout) 문제를 만들고 검증하는 Claude Code harness.

## 개요

출제자가 지문이나 테스트케이스(TC)를 주면 Claude가 아래를 대신한다.

- **지문 검토**: 논리 오류, 모호한 문장, 빠진 조건을 찾는다. 오탈자는 바로 고치고 출제 의도가 걸린 것은 근거와 선택지를 붙여 묻는다.
- **TC 생성**: 정답·오답 풀이, 입력 생성기, 입력 검사기(validator)를 만들고 숨은 TC를 만든다.
- **TC 검증**: 주어진 TC가 맞는지(A), 틀린 풀이를 떨어뜨릴 만큼 강한지(B), 시간 제한이 적절한지 검사한다.

판정은 AI가 아니라 `scripts/`의 스크립트가 내린다. `.out`은 정답 풀이를 실행해서 만들고, AI가 손으로 쓰지 않는다.

품질을 지키는 장치:

| 장치 | 하는 일 |
|---|---|
| blind-solver 에이전트 (2개) | 지문과 예제만 보고 brute-force를 따로 쓴다. 두 풀이와 정답을 작은 랜덤 입력으로 대조해 지문이 두 가지로 읽히는 곳과 정답 버그를 찾는다 |
| validator-writer 에이전트 | 생성기를 쓴 쪽과 다른 쪽이 입력 검사기를 쓴다 |
| wrong-solver 에이전트 | TC를 보지 않고 학생이 낼 법한 틀린 풀이를 쓴다. TC가 이걸 모두 떨어뜨려야 한다 |
| 변이 테스트 (`scripts/mutate.py`) | 정답을 한 글자씩 바꾼 풀이 중 TC는 통과하지만 brute와 다른 것을 찾아 TC 구멍을 알려 준다 |
| 가드 훅 (`scripts/agent_guard.py`) | 위 에이전트들이 정답·TC를 보지 못하게 파일 접근을 막는다 (실수 방지용 린트이고 보안 경계는 아니다) |

## 준비

- Claude Code
- `g++` (C++17), `python3`

## 사용법

### 1. 열기

이 폴더에서 아래처럼 연다.

```
claude --setting-sources project,local --strict-mcp-config
```

사용자 전역 플러그인·MCP·훅을 빼고 이 폴더의 설정(스킬, 에이전트, 가드 훅)만 쓴다. 그냥 `claude`로 열어도 동작한다. 하지만 그러면 전역 플러그인의 스킬 목록과 MCP 도구 이름이 매 요청에 실린다. 그래서 첫 요청 문맥이 약 1.8만 토큰에서 3.8만 토큰으로 두 배가 되고, 요청마다 이 문맥을 다시 읽으므로 비용도 그만큼 는다 (2026-10-13 측정).

모델은 `--model`로 고른다. 평가 세트로 Opus, Sonnet, Haiku를 모두 확인했고 결과는 아래와 같다 (2026-10-13).

| 모델 | 지문 결함 5개 | 약한 TC 찾기 (3번 모드) | 지문 검토 1회 비용 |
|---|---|---|---|
| Opus 5.5 | 10/10 (2회씩) | 찾음 | 약 $0.5 |
| Sonnet 5.5 | 5/5 | 찾음 | 약 $0.07 |
| Haiku 5.5 | 5/5 | 찾음 | 약 $0.02 |

Haiku로 2번 모드 전체(지문 검토부터 TC 생성까지)를 돌린 결과도 확인했다. 비용은 $0.07이었고, 만든 TC에서 평가 세트의 오답 풀이 4개가 모두 떨어졌다. 모델마다 몇 번씩만 돌린 결과이므로, 중요한 문제는 사람이 마지막에 검토한다.

### 2. 요청하기

자연어로 요청하면 `test-problem-maker-start` 스킬이 입력을 보고 단계를 고른다.

| 준 것 | 모드 | 진행 |
|---|---|---|
| 지문(+예제) | 2 | 지문 검토 → TC 생성 → TC 검증 |
| 지문 + TC | 3 | TC 검증 |
| 풀이 방식 + 키워드 + 난이도 | 1 | **아직 구현하지 않음** |

예:

```
이 문제 지문을 검토해줘. 지문은 inbox/problem.md, 예제는 inbox/examples/ 에 있어.
```
```
이 문제의 테스트케이스를 검증해줘. 지문은 inbox/problem.md, 예제는 inbox/examples/, 테스트케이스는 inbox/tests/ 에 있어.
```

예제와 TC는 `1.in`/`1.out`처럼 번호를 붙인 짝으로 둔다.

### 3. 결과

`problems/<슬러그>/`에 문제 폴더가 생긴다 (git에는 넣지 않는다). 구조는 `rules/package.md`에 있다.

- `report.md`: 스크립트 판정(출력 그대로), [수정]/[질문] 목록, 사람이 확인할 것
- `tests/`: 채점용 TC (`N.in`/`N.out`)
- `meta.json`: 시간·메모리 제한
- `state.md`: 진행 단계. 중간에 끊겨도 다음에 이어서 한다

[질문]에 답하면 지문에 반영하고 다시 검토한다. 마지막 검토는 사람이 한다. 특히 `sol/README.md`의 정답 근거와, validator가 본 변수 범위가 지문과 같은지 확인한다.

### 스크립트만 직접 쓰기

AI 없이도 쓸 수 있다. 사용법과 출력 문구는 각 스크립트 맨 위 설명에 있다.

```
python3 scripts/run.py P sol/x.cpp          # 풀이 하나 채점
python3 scripts/validate.py P               # 입력 검사기로 모든 입력 검사
python3 scripts/make_outputs.py P           # 정답으로 .out 만들기
python3 scripts/stress.py P --gen "8 {seed}" # 정답과 brute 랜덤 대조
python3 scripts/verdicts.py P               # 모든 풀이의 기대 판정, 시간 제한 추천
python3 scripts/mutate.py P --gen "8 {seed}" # 변이 테스트로 TC 구멍 찾기
```

## 폴더

```
CLAUDE.md            Claude가 처음 읽는 안내
rules/               원칙, 문제 폴더 규약, 결정 기록
.claude/skills/      start(진입점), statement-review, testgen, testcheck, generate(미구현)
.claude/agents/      blind-solver, validator-writer, wrong-solver
scripts/             판정 스크립트와 가드 훅
templates/problem/   문제 폴더 템플릿
tests/               스크립트 회귀 테스트
eval/                평가 세트: 정상 문제 3개와 결함 케이스
docs/                설계 기록(spec.md)과 출제 과정 리서치
```

## harness를 고칠 때

`DEVELOPMENT.md`를 따른다. 스크립트를 고치면 아래 둘을 통과해야 한다.

```
python3 tests/run_tests.py   # 회귀 테스트
python3 eval/run_eval.py     # 평가 세트 (약 5분): 정상 문제 오탐 0, 결함 케이스 전부 잡음
```

## 한계

- 1번 모드(문제 생성)는 아직 없다.
- 시간 측정값은 실행한 컴퓨터 기준이다. Zukbam 채점 서버와 다를 수 있다.
- 변이 테스트와 brute 대조는 작은 입력만 쓴다. 큰 값에서만 드러나는 실수(오버플로)는 전용 TC로 따로 챙긴다.
- 해시 충돌을 노리는 TC(`unordered_map` 저격)는 자동으로 만들지 않는다.
