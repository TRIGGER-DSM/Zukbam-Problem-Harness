# 리서치 1: Codeforces Polygon / testlib

- 조사일: 2026-10-12
- 방법: 원문을 직접 읽음. codeforces.com은 WebFetch가 403이라 curl로 받아 텍스트로 읽음. `codeforces.com/r/...` 링크는 공개 Google Docs로 리다이렉트됨
- ⚠ 표시는 요약 모델을 거쳐 읽었거나 검색 스니펫만 본 것 (인용이 정확하지 않을 수 있음)
- 가장 중요한 출처: Codeforces 라운드 출제자 공식 규칙 https://codeforces.com/r/authors-polygon-rules (이하 "Polygon rules")

## 1. Validator (입력 검사)

1. **validator는 필수이고 지문의 모든 제약을 검사한다.** "Validators are strictly required for problems on Codeforces." 근거: "Even experienced problem setters make mistakes sometimes (for example, in the prestigious ACM ICPC World final 2007)." — https://codeforces.com/blog/entry/18426
2. **공백·줄바꿈까지 엄격하게.** "Validator is strict. It cares about correct placing of spaces." readSpace/readEoln/readEof를 명시적으로 호출 — https://codeforces.com/blog/entry/18426
3. **선행 0, 줄 끝도 최대한 엄격하게.** "Validators should be maximally strict with respect to spaces, endlines, leading zeroes etc", "It also validates that the file ends with EOLN and EOF." — https://codeforces.com/testlib , https://github.com/MikeMirzayanov/testlib
4. **범위 검사에 지문과 같은 변수 이름을 붙인다.** "In the validator read*() statements, the variable name should be exactly the same as in the statement." — Polygon rules, blog 18426
5. **합 제약(sum of n)은 테스트케이스마다 검사, 구조 조건(자기 루프 없음 등)도 명시적으로 검사.** "Check the limit on the sum of n after each test case." MAXN과 MAX_SUM_N 상수를 분리 — Polygon rules, IgorI "Polygon hints" https://docs.google.com/document/d/172KYkws5YfsmEr0ymR-1tAwsnHtzgcS2CQ_KhnLC_GQ
6. ⚠ **validator 자체도 테스트한다.** 각 검사를 경계 바로 안/밖 값으로 확인. "we can consider the validator correct when it produce the correct verdict and error message" — https://quangloc99.github.io/posts/polygon-codeforces-tutorial/

## 2. Generator와 테스트 설계

7. **generator는 결정적이고 재현 가능해야 한다.** "a generator must output the same test when compiled by any compiler on any platform if it is run in the same way". 시드는 명령줄 인자 전체의 해시 — https://codeforces.com/blog/entry/18291
   - (추론, 출처 아님) Python `random`은 버전에 따라 결과가 바뀔 수 있으므로 버전 고정 또는 자체 난수 생성기가 안전함
8. **입력 형식을 정확히 지키고 줄바꿈으로 끝낸다.** "The test should end with a line feed." — blog 18291
9. **한 번 실행에 테스트 하나, 의미 있는 이름, 시드만 바꾼 반복 금지.** "Do not use a generator with the same parameters (but different seeds) more than once." 나쁜 이름 `gen1`, 좋은 이름 `gen_path` — Polygon rules
10. **예제는 손으로, 나머지는 생성. 예제 다음 테스트는 가능한 작은 경우 전부.** "The first test after examples ... should list all possible small tests. Start from the smallest possible test case (typically n=1)" — Polygon rules
11. **모든 변수의 최소·최대·중간값과 그 조합.** "Always make tests (at least) with minimum possible, maximum possible, and some value in between for each variable and their combinations." — Polygon rules
12. **표준 generator 분류**: `gen_rand`, `gen_all_small`, `gen_handmade`, `gen_fail_*`(특정 오답을 WA/TL/ML/RE로 만드는 것), `gen_max_io`. 답을 최대/최소로 만드는 테스트, 입출력 글자 수를 최대로 만드는 테스트, "0101…010", "0000…01…1111" 같은 패턴 — IgorI doc
13. **트리 등은 모양을 의도적으로.** `rnd.wnext(i, t)`로 경로형/별형 조절 후 정점 번호와 간선 순서를 섞음 — blog 18291
14. **anti-hash 테스트.** unordered_map 충돌로 O(n²) 유도, mod 2^64 다항 해시 깨기 — https://codeforces.com/blog/entry/62393 , ⚠ https://codeforces.com/blog/entry/4898 (스니펫만)

## 3. 정답·오답·느린 풀이 (기대 판정 태그)

15. **주 정답: 상수 최적화 없이, 시간·메모리 제한의 절반 이하.** "It should use at most half TL and half ML." 다른 저자가 쓴 정답도 하나 이상 — Polygon rules
16. **지문을 그대로 따라 하는 brute-force는 TLE 태그.** "A stupid bruteforce solution that does exactly what is written in the statements. Make sure it only gives OK or TL" — Polygon rules
17. **떨어뜨릴 느린 풀이는 최대한 최적화하고도 2배 TL을 넘어야.** "Optimize them as much as you can, including using pragmas. These solutions should not fit double TL or ML." — Polygon rules
18. **오버플로 지점마다 오답 풀이 하나.** "add one for each variable/array/place in code where overflow can occur. Make sure they all fail" — Polygon rules
19. **경우 나누기가 있으면 각 경우를 주석 처리한 오답 풀이 하나씩.** — Polygon rules
20. ⚠ 입력에 따라 판정이 다른 풀이는 "Incorrect" 태그 — quangloc99 튜토리얼

## 4. 시간 제한과 여러 언어

21. 출처: Polygon rules, 체크리스트 https://codeforces.com/r/authors-polygon-checklists
    - 주 정답 ≤ TL의 절반, 떨어뜨릴 느린 풀이 > TL의 2배
    - Python: "For easy problems write a solution in Python and make sure it passes without any optimizations."
    - "If possible, do not make tight limits. For harder problems, 2 seconds TL is the minimum possible."
    - Java: C++ 풀이가 TL의 ¼ 이상 걸리면 Java 정답도 필요
22. **stress 테스트 최소 2개.** 큰 랜덤 입력으로 정답끼리, 작은 랜덤 입력으로 brute-force와. "Make sure the stress generators can produce all possible tests, e.g., the n value is not limited to a fixed value, the array elements are not limited to be distinct ..., the graph is not limited to be connected" — Polygon rules

## 5. Checker

23. **표준 checker 우선.** "Do not validate the input file in the checker." "Do not check for whitespace unless you need to." — Polygon rules
24. **readAns 패턴: 심사 답과 참가자 출력을 같은 함수로 읽는다.** 참가자 답이 심사 답보다 좋으면 `_fail`(심사 오류) — https://codeforces.com/blog/entry/18431
25. **참가자 값은 전부 범위 검사.** "There will surely be a contestant who will output -42, 2147483456 or some other garbage" — blog 18431
26. **checker 테스트 작성.** 참가자 답이 심사 답보다 좋은 경우 포함, 모든 종료 경로를 덮기 — 체크리스트, IgorI doc

## 6. 지문

27. Polygon rules, IgorI doc:
    - 예제: 출력 형식마다 하나 이상, 문제당 2개 이상, 최소 2개에 설명(note). 헷갈릴 만한 예제마다 설명
    - 입력 절: "One paragraph should correspond to one line of the input. Give constraints on each value in parentheses right after its appearance in the input format."
    - 같은 변수 이름을 다른 대상에 재사용하지 않음, 표준 문구("It is guaranteed that...", "If there are multiple solutions, print any of them.")
    - "Avoid using something that is not defined yet", "Avoid using unnamed objects"

## 7. 검수 과정

28. 코디네이터 검토 → 테스트 전에 저자가 지문·validator·checker·정답·brute-force·stress·랜덤 테스트 준비 → 테스터가 가상 참가로 풀이 → 저자가 더 강한 테스트와 오답 풀이 추가. "Each problem has a full solution not written by the author". 테스터는 지문이 명확했는지("Did anything require careful re-reading?") 보고하고 "Wrong greedy, hacky cutoffs, suboptimal solutions with pragmas"를 시도 — https://codeforces.com/r/authors-guide , https://codeforces.com/r/testers-instructions

## 주의
- 멀티테스트 강제(t ≤ 10^4), pretests = tests, 문제별 테스트 수 제한은 Codeforces 라운드 전용 규칙이라 그대로 적용하지 않음
- Polygon 문서 자체에는 "TL = 정답 시간 × k" 규칙이 없음. 절반/2배 규칙은 라운드 규칙에서 나옴
