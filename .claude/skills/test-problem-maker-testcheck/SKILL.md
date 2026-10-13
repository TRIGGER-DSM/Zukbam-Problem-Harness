---
name: test-problem-maker-testcheck
description: TC가 맞는지(A)와 충분히 강한지(B)를 검사하고 최종 리포트를 만든다. test-problem-maker-start만 호출한다.
---

# test-problem-maker-testcheck

먼저 `rules/principles.md`, `rules/package.md`를 읽는다. `P`는 문제 폴더다.
스크립트 출력은 고치지 않고 `report.md`에 그대로 붙인다.

## 0. 빠진 부품 채우기 (3번 모드에서 사용자가 지문과 TC만 줬을 때)
- `validator.py`가 없으면 `test-problem-maker-validator-writer`에게 쓰게 한다.
- `sol/main.cpp`가 없으면 직접 쓴다 (`test-problem-maker-testgen` 1절과 같게).
- `sol/brute.cpp`가 없으면 `test-problem-maker-blind-solver`에게 쓰게 한다.
- `gen/gen.py`가 없으면 stress용 작은 입력 생성기를 쓴다.
- **사용자가 준 `tests/`의 `.in`·`.out`은 고치지 않는다.**

## A. TC가 맞는가
1. `python3 scripts/check_package.py P`
2. `python3 scripts/validate.py P`
   - `validator 거부: tests/N.in` → 사용자 TC가 지문 제약을 어긴다. validator가 맞는지 먼저 확인하고, 맞으면 [질문]으로 보고한다.
   - `형식 문제`, `중복 입력` → [수정] 제안으로 보고한다 (직접 고치지 않는다).
3. `python3 scripts/make_outputs.py P`
   - `정답과 다름: <TC>` → **어느 쪽이 맞는지 정하지 않는다.** 그 TC가 크면 stress로 같은 불일치를 내는 작은 입력을 찾아, 입력·사용자 출력·우리 정답 출력을 함께 [질문]으로 보여준다.
4. `python3 scripts/stress.py P --gen "<작은 입력 {seed}>" --count 200` — 우리 정답 자체를 믿을 수 있는지 확인한다.

A에서 [질문]이 남았으면 B로 가지 않고 보고한다. 정답이 확정되지 않으면 B의 결과를 믿을 수 없다.

## B. TC가 충분히 강한가
1. 떨어뜨릴 풀이가 `sol/wrong_answer/`, `time_limit_exceeded/`에 없으면 `test-problem-maker-wrong-solver`에게 문제 폴더 경로만 주고 쓰게 한다. 직접 쓰지 않는다 (TC를 본 쪽이 쓰면 TC에 맞춘 풀이가 된다).
2. `python3 scripts/verdicts.py P`
   `python3 scripts/mutate.py P --gen "<A-4의 작은 입력 {seed}>"`
3. 결과 해석:
   - `기대와 다름: sol/wrong_answer/X — 오답이(가) 한 번도 안 나옴` → **TC가 약하다.** 어떤 실수가 통과했는지 보고한다.
   - `TC 구멍: <변이> — <인자>` → **TC가 약하다.** 그 변이를 잡는 입력의 생성 인자와 함께 보고한다.
   - `시간 제한 문제` → 시간 제한이나 TC 크기를 조정해야 한다. 추천값과 함께 보고한다.
4. 사용자 TC를 보강할지 [질문]한다. 승인하면 생성기로 그 풀이·변이를 잡는 TC를 만들어 `gen_tests.py P --start <사용자 TC 다음 번호>`로 **뒤에 추가**하고 2번부터 다시 한다.

## C. 난이도 가늠 (`meta.json`의 `difficulty`가 있을 때)
1. `test-problem-maker-fast-solver`를 **Agent 도구의 `model: "haiku"`로** 불러 `sol/probe-haiku.cpp`에 쓰게 한다 (문제 폴더 경로와 파일 경로만 준다).
2. `python3 scripts/run.py P sol/probe-haiku.cpp`
3. 판정이 아니라 신호로만 보고한다 (`rules/generate.md`의 "난이도 신호"):
   - 목표가 플래티넘 이상인데 전부 통과 → "목표보다 쉬울 수 있음"
   - 목표가 실버 이하인데 못 풂·실패 → "목표보다 어렵거나 지문이 부족할 수 있음"
   - 그 밖은 그대로 적는다

## 끝 보고 (report.md)
- A·B 각 스크립트의 마지막 출력 (그대로)
- stress 대조 횟수와 불일치 여부
- 통과해버린 오답 풀이 목록과 `TC 구멍` 목록 (TC가 약한 곳), `동등 추정` 목록
- [수정] 제안, [질문] 목록
- "측정값은 이 컴퓨터 기준"이라는 문장
- 사람이 확인할 것: `sol/README.md`의 정당성 근거, 지문과 validator의 범위 대조 (`validate.py`의 `범위:` 줄과 지문을 나란히)

`state.md`의 `stage`를 `checked`로 바꾼다.
