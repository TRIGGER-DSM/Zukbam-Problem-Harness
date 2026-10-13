# Zukbam Problem Harness

학교 코딩테스트 사이트 Zukbam에 올릴 문제를 Claude Code로 검토하고 테스트케이스(TC)를 만드는 도구입니다.
문제는 백준처럼 표준 입력으로 받고 표준 출력으로 답하는 형식입니다.

## 무엇을 해 주나요

- **지문 검토**: 빠진 조건, 두 가지로 읽히는 문장, 예제와 맞지 않는 설명을 찾습니다. 오탈자는 바로 고치고, 출제 의도에 따라 답이 달라지는 것은 근거와 선택지를 붙여 물어봅니다.
- **TC 만들기**: 정답 풀이, 입력 생성기, 입력 검사기를 만들고 채점용 TC를 만듭니다.
- **TC 검증**: 가지고 있는 TC의 답이 맞는지, 흔히 하는 실수를 떨어뜨릴 만큼 강한지, 시간 제한이 적절한지 확인합니다.

통과·오답 같은 판정은 AI가 아니라 `scripts/`의 스크립트가 내립니다. TC의 정답 출력도 AI가 직접 쓰지 않고 정답 풀이를 실행해서 만듭니다.

## 준비

- [Claude Code](https://docs.claude.com/en/docs/claude-code)
- `g++` (C++17), `python3`

## 사용법

### 1. 열기

이 폴더에서 Claude Code를 엽니다.

```
claude --setting-sources project,local --strict-mcp-config
```

이렇게 열면 개인 환경에 설치한 플러그인과 MCP 서버를 빼고 이 폴더의 설정만 씁니다. 그만큼 토큰을 덜 씁니다. 그냥 `claude`로 열어도 동작합니다.

### 2. 요청하기

지문과 예제 파일을 아무 폴더에나 두고, 위치를 알려 주며 요청합니다.

**지문만 있을 때** (지문 검토 → TC 만들기 → TC 검증)

```
이 문제로 테스트케이스까지 만들어줘. 지문은 inbox/problem.md, 예제는 inbox/examples/ 에 있어.
```

**지문 검토만 받고 싶을 때**

```
이 문제 지문을 검토해줘. 지문은 inbox/problem.md, 예제는 inbox/examples/ 에 있어.
```

**지문과 TC가 이미 있을 때** (TC 검증)

```
이 문제의 테스트케이스를 검증해줘. 지문은 inbox/problem.md, 예제는 inbox/examples/, 테스트케이스는 inbox/tests/ 에 있어.
```

예제와 TC는 `1.in`·`1.out`, `2.in`·`2.out`처럼 번호를 붙인 짝으로 둡니다.

진행 중에 출제 의도를 물어보는 [질문]이 나오면 답해 주세요. 답을 지문에 반영하고 이어서 진행합니다. 가지고 온 TC는 고치지 않고, 보강이 필요하면 추가할지 먼저 묻습니다.

### 3. 결과 보기

`problems/<문제 이름>/` 폴더가 생깁니다.

| 파일 | 내용 |
|---|---|
| `problem.md` | 검토를 반영한 지문 |
| `tests/` | 채점용 TC (`N.in`, `N.out`) |
| `meta.json` | 시간·메모리 제한 |
| `report.md` | 검토 결과, 스크립트 판정, 사람이 확인할 것 |
| `sol/` | 정답 풀이와 떨어뜨려야 할 오답 풀이 |
| `state.md` | 진행 단계. 중간에 끊겨도 다음에 이어서 합니다 |

마지막 확인은 사람이 합니다. `report.md`의 "사람이 확인할 것"과 `sol/README.md`의 정답 근거를 읽어 주세요.

### 스크립트만 쓰기

AI 없이 스크립트만 쓸 수도 있습니다. `P`는 문제 폴더입니다. 자세한 사용법은 각 파일 맨 위 설명에 있습니다.

```
python3 scripts/run.py P sol/x.cpp           # 풀이 하나 채점
python3 scripts/validate.py P                # 모든 입력이 지문 제약을 지키는지
python3 scripts/make_outputs.py P            # 정답 풀이로 .out 만들기
python3 scripts/verdicts.py P                # 모든 풀이 채점, 시간 제한 추천
```

## 아직 안 되는 것

- 풀이 방식·키워드·난이도만 주고 새 문제를 만드는 기능은 아직 없습니다.
- 시간은 이 컴퓨터에서 잰 값입니다. Zukbam 채점 서버와 다를 수 있습니다.

## 폴더 구조

```
CLAUDE.md            Claude가 처음 읽는 안내
rules/               원칙, 문제 폴더 규칙, 결정 기록
.claude/skills/      단계별 절차 (진입점은 test-problem-maker-start)
.claude/agents/      정답을 보지 않고 따로 일하는 보조 에이전트
scripts/             판정 스크립트
templates/problem/   문제 폴더 템플릿
tests/, eval/        harness 자체를 검사하는 테스트와 평가 세트
docs/                설계 기록과 출제 과정 조사
```

harness 자체를 고치려면 `DEVELOPMENT.md`를 보세요.
