# 리서치 2: ICPC / Kattis / BAPCtools / IOI 출제 지침

- 조사일: 2026-10-12
- 방법: 1차 자료 9개를 직접 읽음 (Kattis 문제 패키지 규격 2025-09·legacy, problemtools 소스, BAPCtools 문서, ICPC 심사 지침 2026-06 PDF, ICPC WF Judging Notes, IOI 2022 HSC 보고서)
- 공개 1차 자료를 못 찾은 것: AtCoder 작성자 가이드, Code Jam/Kick Start, USACO 가이드

주요 출처 약칭:
- Kattis spec: https://www.kattis.com/problem-package-format/spec/2025-09.html
- ICPC PDF: https://u.icpc.global/wp-content/uploads/2026/08/ICPC-JudgingGuidelines-20260619.pdf
- IOI 보고서: https://ioi2022.id/data/ioi-2022-hsc-report.pdf
- BAPCtools: https://github.com/RagnarGrootKoerkamp/BAPCtools (docs/*.md)
- problemtools: https://github.com/Kattis/problemtools (problemtools/checks/*.py)

## A. 시간 제한 산정

1. **양쪽 여유.** "T_ac * ac_to_time_limit <= time_limit and time_limit * time_limit_to_tle <= T_tle." 기본값 ac_to_time_limit 2.0, time_limit_to_tle 1.5. TLE 제출물이 없으면 T_tle은 무한대 — Kattis spec
2. **해상도 단위로 올림.** 조건을 만족하는 time_resolution(기본 1.0초)의 최소 정수배. 그런 값이 없으면 오류. "avoid specifying time_limit whenever practical" — Kattis spec
3. **기준 시간은 테스트 전체 중 가장 느린 실행 시간.** TLE가 필수인 제출물이 상한, TLE가 허용되지 않는 제출물이 하한. brute_force는 산정에서 빠짐 — Kattis spec
4. 구 규격 기본값: time_multiplier 5, time_safety_margin 2 — https://www.kattis.com/problem-package-format/spec/legacy.html
5. **problemtools 구현.** `max(1, ceil(가장 느린 AC × ac_to_time_limit / 해상도)) × 해상도`. 고정 TL이 이보다 작으면 오류. TL 근처에서 결과가 뒤집히는 제출물은 "is sensitive to time limit" 경고 — problemtools checks/submissions.py
6. BAPCtools `bt time_limit`도 같은 두 배수로 TL을 정하고 `--write`로 기록 — BAPCtools docs/commands/development.md
7. **ICPC.** 통과해야 할 레퍼런스 중 가장 느린 것과 너무 느린 것으로 간주할 것 중 가장 빠른 것의 시간을 보고, "The time limit is set to a value in between these times." — ICPC PDF
8. **다언어.** "every problem should have reference solutions in at least two of those language families within the given time and memory limits. There is no guarantee that every problem can be solved ... in every language." — ICPC PDF

## B. 기대 판정별 제출물과 자동 검증

9. **폴더별 규칙.** accepted: 허용 [AC] / wrong_answer: 허용 [AC, WA], 필수 [WA] / time_limit_exceeded: 허용 [AC, TLE], 필수 [TLE] / run_time_error: 허용 [AC, RTE], 필수 [RTE] / brute_force: 허용 [AC, RTE, TLE], 필수 [RTE, TLE]. 정답 하나 이상 필수 — Kattis spec
10. **판정 규칙.** "all test cases must have only verdicts present in permitted; at least one test case must have a verdict in required". submissions.yaml로 테스트 그룹별 기대 판정 지정 가능 — Kattis spec
11. **떨어뜨릴 풀이는 실제로 구현해 본다.** "The alternative solutions must fail the tests ... even if they were otherwise cleverly coded! You may sometimes be surprised how 'good' unintended solutions turn out to be." — ICPC PDF
12. **독립적으로 쓴 정답 하나 이상.** "at least one additional full solution written independently from the model solution ... the authors were discouraged to collaborate." — IOI 보고서
13. BAPCtools `bt run`: 모든 제출물 × 모든 케이스, 예상과 다른 결과만 한 줄씩 출력. `--table`로 어떤 케이스를 어떤 제출물이 풀었는지 표. `--sanitizer`로 C++ sanitizer — BAPCtools development.md

## C. 입력 validator

14. 성공 시 종료 코드 42, 모든 테스트 케이스에 실행. BAPCtools는 실패 시 정확히 43 요구 — Kattis spec, BAPCtools docs/advanced/validation.md
15. **엄격함을 자동으로 시험.** validator가 다음을 거부하지 않으면 경고: 빈 파일, 랜덤 바이너리, 랜덤 ASCII, 기존 테스트에 공백 추가, 줄 끝 공백 추가, 줄바꿈 추가, 정수 선행 0 추가, 소수 끝 0 추가, 파일 끝에 쓰레기 추가. 경고 문구 "No validator rejects {desc}" — problemtools checks/validators.py
16. **일부러 잘못된 케이스 폴더.** "Each tc.in under invalid_input must be rejected by at least one input validator." 예: negative, too_large, not_a_number, extra input, trailing whitespace — Kattis spec, BAPCtools validation.md
17. **답 파일(.ans)도 형식·범위 검증** (정답 여부는 아님) — BAPCtools validation.md
18. **validator는 generator와 다른 사람이 쓴다.** "so that the test data generator and the test data validator are written by different authors." — IOI 보고서. ICPC는 의미 제약(좌표 순서 등)까지 검사 요구 — ICPC PDF
19. **경계값 도달 확인.** `bt constraints`: validator의 범위가 실제 데이터에서 도달됐는지 ("BOUND NOT REACHED: ... never equal to the upper bound of 1000. Max value found: 999"), 지문과 validator의 경계를 나란히 보여 사람이 대조 — BAPCtools docs/commands/validation.md

## D. 출력 비교 / checker

20. 기본 checker는 "essentially a beefed-up diff": 공백 기준 토큰 비교, 대소문자·공백 민감 옵션, 실수 오차 옵션. 커스텀 checker는 WA 시 43, 그 외 코드는 checker 오류 — Kattis spec
21. **checker를 쓰레기 출력으로 시험.** `-1`, `2147483648`, `9223372036854775808`, `NaN`, `inf`, `\x00`, `1/0` — problemtools validators.py
22. **심사 답 파일이 checker에서 정답을 받는지 확인** — problemtools checks/testdata.py

## E. 테스트 데이터 구성

23. sample과 secret 분리, secret 필수. 같은 입력 파일 중복 경고, .in/.ans 짝 불일치 오류, '\n'으로 끝나지 않거나 '\r'이 있으면 경고 — Kattis spec, problemtools testdata.py
24. **개수.** "BAPCtools encourages to use 30-100 test cases." 예제 2개 이상 — https://ragnargrootkoerkamp.github.io/BAPCtools/workflow/
25. **경계 케이스 포함, 찍어서 맞히기 방지.** yes/no처럼 출력 종류가 적으면 "Produce sufficient separate test case input files" — ICPC PDF
26. **결정적 생성과 퍼징.** `bt generate --check-deterministic`, `bt fuzz`(시드를 바꿔 정답 풀이를 랜덤 데이터로 돌리고 실패 케이스 기록) — BAPCtools development.md, docs/generators.md

## F. 지문 품질

27. **완전하고 모호하지 않게.** "specify a problem completely and unambiguously ... Ideally, no clarification request should need to be answered." 관용 표현 최소화, 입력 개수와 범위 명시, "The output must be specified as much as necessary, considering such oddities as trailing blanks, leading zeroes, empty lines, etc." 구성: 스토리 → 비형식 설명 → 정밀한 입출력 형식 → 예제 — ICPC PDF. "The problem statement will specify the format and bounds for all input data" — https://image.icpc.global/wf2026/doc/Judging-Notes.pdf
28. **IOI 체크리스트.** "Check that sample test cases written in the task statement match the public files." "Check that all variables introduced in the task statement have Constraints." 출제자가 아닌 proofreader·beta tester: "people who have not known the task before can correctly understand the task from the task statement". 직전에 "check that all verdicts are intended" 재실행 — IOI 보고서. Kattis는 지문에 예제를 직접 쓰지 않고 시스템이 예제 파일을 붙임 (어긋남 방지) — Kattis spec
