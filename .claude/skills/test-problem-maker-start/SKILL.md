---
name: test-problem-maker-start
description: 코딩테스트 문제 생성·지문 검토·테스트케이스 생성/검증 요청의 유일한 진입점. 입력을 보고 시작 단계를 고르고, 진행 상태를 기록하고, 끝 보고를 한다.
---

# test-problem-maker-start

먼저 `rules/principles.md`와 `rules/package.md`를 읽는다.

**직접 검토하거나 만들지 않는다.** 요청이 "지문 검토만"이어도 반드시 3절대로 문제 폴더를 만들고, 4절의 스킬을 Skill 도구로 호출해 그 절차를 따른다. 혼자 읽고 판단한 결과는 독립 풀이 대조와 스크립트 판정이 없어서 보고할 수 없다.

## 0. 모델 정하기 (`harness.local.json`이 없거나, 사용자가 바꾸자고 할 때)
AskUserQuestion으로 두 가지를 묻는다 (쓸 수 없는 환경이면 같은 선택지를 글로 묻는다).
1. 주로 쓸 메인 모델: **Sonnet (추천, Pro 요금제)** / Opus (품질 우선, Max 요금제) / Haiku (가장 적은 토큰, 품질이 떨어질 수 있음)
2. 보조 에이전트(blind-solver, validator-writer, wrong-solver, fast-solver) 모델: **Haiku (추천, 토큰 절약)** / 메인과 같게

답을 받으면:
- `harness.local.json`에 `{"main_model": "<sonnet|opus|haiku>", "helper_model": "<haiku|sonnet|opus|same>"}`을 쓴다.
- `.claude/settings.local.json`에 `{"model": "<메인 모델>"}`을 쓴다 (파일이 있으면 `model`만 바꾼다). 다음에 열 때부터 적용된다.
- 사용자에게 알린다: "지금 대화의 모델은 바로 바뀌지 않아요. 바로 바꾸려면 `/model <메인 모델>`을 입력해 주세요."
- 그다음 원래 요청으로 돌아간다.

## 1. 이어서 하는지 확인
`problems/*/state.md` 중 `stage: done`이 아닌 것이 있으면 사용자에게 이어서 할지 묻는다. 이어서 하면 그 `state.md`의 `다음 할 일`부터 진행한다.

## 2. 입력 판별

| 사용자가 준 것 | 모드 | 시작 스킬 |
|---|---|---|
| 풀이 방식 + 키워드 + 난이도 (기존 문제 변형 포함) | 1 | `test-problem-maker-generate` → `test-problem-maker-statement-review` → `test-problem-maker-testgen` → `test-problem-maker-testcheck` |
| 지문만 | 2 | `test-problem-maker-statement-review` → `test-problem-maker-testgen` → `test-problem-maker-testcheck` |
| 지문 + 테스트케이스 | 3 | `test-problem-maker-testcheck` |

- 세션을 시작하면 사용자에게 메뉴가 보인다 (`scripts/welcome.py`). 사용자가 번호로 답하면: 1 → 1번 모드, 2 → 2번 모드, 3 → 2번 모드의 지문 검토까지만, 4 → 3번 모드, 5 → 이어서 하기(1절).
- 그 모드에 필요한 것이 빠졌으면 빠진 것만 묻는다. 선택지가 있는 질문(난이도, 풀이 방식 등)은 AskUserQuestion으로 고르게 하고, 예시를 붙인다.
- 판별이 애매하면 메뉴의 선택지로 묻는다.
- 여러 문제를 한 번에 요청하면 문제마다 아래 3~5를 따로 한다.

## 3. 문제 폴더 만들기
1. 슬러그를 정한다: 영어 소문자와 `-`만 (예: `ant-charger`).
2. `templates/problem/`을 `problems/<슬러그>/`로 복사한다.
3. 사용자가 준 지문은 `problem.md`에, 예제는 `examples/N.in`·`N.out`에, TC는 `tests/N.in`·`N.out`에 넣는다. 내용은 고치지 않고 그대로 넣는다.
4. `meta.json`을 채운다. `mode`에는 위 표의 모드를 넣는다. 아직 모르는 값(시간 제한 등)은 템플릿 값으로 둔다.
5. `state.md`에 `mode`와 `다음 할 일`을 적는다.

## 4. 단계 실행
위 표의 순서대로 스킬을 호출한다. 단계가 끝날 때마다 `state.md`의 `stage`와 `다음 할 일`을 고친다.

호출할 스킬이 **미구현**이라고 적혀 있으면 거기서 멈추고 사용자에게 "<스킬> 단계는 아직 준비되지 않았다"고 알린다. 그 단계를 대신 지어내서 하지 않는다.

## 5. 끝 보고
1. `python3 scripts/check_package.py problems/<슬러그>`를 실행하고 출력을 `report.md`에 붙인다.
2. `stage: done`으로 바꾼다.
3. 사용자에게 보고한다: 무엇을 만들었는지/고쳤는지, 스크립트 판정(출력 그대로), 몇 개 입력으로 대조했는지와 갈린 적이 있었는지, 사람이 확인해야 할 것, 남은 [질문].
