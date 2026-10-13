# 리서치 3: 국내 출제 자료, 실패 사례, LLM 테스트 생성 연구

- 조사일: 2026-10-12
- [스니펫만] = 검색 결과 요약만 봄. 나머지는 원문을 직접 읽음
- 접속 문제: acmicpc.net 도움말·게시판은 404. kitpa 기사에 따르면 BOJ는 2026-04-28 서비스 종료 (https://kitpa.org/news/1366). Codeforces 블로그는 공식 API로 본문을 받음

## 1. 국내 자료

1. **UCPC 지문 컨벤션.** '자연수' 대신 '양의 정수'/'음이 아닌 정수'. 제한은 [입력]에서 변수가 처음 나오는 곳에 부등식으로. 한 번만 입력받는 변수는 대문자, 나머지는 소문자. 수열 인덱스는 1부터. 큰 수는 세 자리마다 띄어 씀(1 000 000 007) — https://github.com/ucpcc/problemsetting-guidelines
2. **UCPC 입출력 형식.** EOF로 끝을 알리는 형식과 공백 포함 문자열 입력은 피함. "공백을 사이에 두고 주어진다"처럼 구분 방식 명시. '첫째 줄', 'i째 줄'. 손으로 따라갈 수 있는 작은 예제 최소 하나 — 같은 출처
3. **BOJ 데이터·지문 규칙 (비공식 정리).** "의미없는 공백이 줄의 뒷 쪽에 있으면 안됩니다." "데이터의 모든 줄은 줄 바꿈(\n)으로 끝나야 합니다." UTF-8, .in/.out, 예제는 자동으로 데이터에 추가. 번역체("보장된다") 대신 "만족한다". 답이 여러 개면 유형별 예제. ≤ ≥ ≠ × 사용 — https://github.com/ndb796/BOJ-Problem-Set-Producing
4. [스니펫만] BOJ: "문제 하나 당 최소 3명의 검수자가 필요합니다." — https://help.acmicpc.net/problem/add (현재 404)
5. [스니펫만] BOJ 오류 신고는 크게 "데이터 추가 후 재채점"과 "데이터 수정 후 재채점". 추가 데이터에 공백 문자가 섞여 런타임 에러가 난 사례 → 추가 데이터도 validator를 다시 통과해야 함 — help.acmicpc.net/judge/info, acmicpc.net/board/view/18974 (현재 404)
6. **Algospot 검수 항목.** 테이블/이미지/마크업 깨짐, 출제자 오류, 데이터 오류, 디스크립션의 모호함/오탈자, 변수 이름 중복 — https://algospot.com/wiki/read/%EB%AC%B8%EC%A0%9C_%EA%B2%80%EC%88%98_%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8
7. **교차 검수 순서와 실제 서버 검수 (숭고한 캠프 2020).** 수학적 오류 → checker·validator → 정답 통과 → 오답 탈락. "폴리곤에서 검수가 완료되었다고 해서 돔저지 서버에서 검수를 하지 않으면 안 됩니다". 마지막 줄 개행 유무만 다른 정답 두 개를 실제 채점 서버에서 돌려 봐야 함(체커 때문에 오답 처리된 사례). 용어·문체를 미리 통일하지 않아 지문 검수가 오래 걸림 — https://cyberflower.github.io/2020/07/21/endofSKH.html
8. **validator는 공백 하나까지.** "공백 하나, 개행 하나도 확실하게 읽고 판단해야 합니다." 흔한 오류: 줄 끝 공백, 마지막 줄 개행 누락. generator 시드는 인자로 고정 — https://infossm.github.io/blog/2021/05/14/testlib/
9. **검수자 체크리스트 (LeetCode 대회 검수자).** 지문 모호함, 의도하지 않은 풀이(DP를 그리디로), 경계값·자료형·메모리 테스트, 느린 풀이를 거르는 제한, 여러 언어 확인. "특정 언어에서 통과되지 않는다면 이를 리포트해 수정 방향을 제시해야 한다." — https://songhayoung.github.io/2024/10/19/DayLife/20241019/
10. **출제진과 검수진 분리 (UCPC 2019).** "이미 풀이를 아는 분들이라 fresh하게 문제를 볼 수 있는 검수진분들이 필요했습니다." 검수 가이드라인을 미리 주지 못한 것을 반성. 사이트로 옮기며 오타 발생 — https://ansubin.com/how-to-organize-large-algorithm-contest-ucpc2019-review/
11. **나는코더다 2019 송년대회.** 지문이 불명확하면 정답률이 떨어짐. 풀리는지 확인하지 않고 후보에 올림. 기존 문제와의 유사성을 거르지 못함. 실수 오차 검증 부족으로 최대 크기 데이터를 못 만듦 — https://youngyojun.github.io/contest/review/2020/02/15/iamcoder-2019-yearend-contest/
12. **스트레스 테스트.** "스스로 만들 수 없는 테스트 케이스도 분명 있기 때문이다." — https://seungwuk98.github.io/%EC%95%8C%EA%B3%A0%EB%A6%AC%EC%A6%98/01-stresstest/

## 2. 실패 사례와 교훈

13. **스트레스 테스트가 있어도 정해가 틀림 (CF Round 421, unrated).** "we had a stress testing between the bruteforce and the main solutions. However, all these measures haven't prevented the mistake" → 정해의 정당성 근거가 따로 필요 — https://codeforces.com/blog/entry/52944
14. **지문이 보장하지 않는 성질의 반례 누락, checker가 조건 하나를 안 봄 (CF Round 637, unrated).** "the numbers d_i were not necessarily sorted, but there were no pretests for that", "The checker ... didn't check one of the requirements" — https://codeforces.com/blog/entry/76506
15. **"Way of problemsetter".** 단순 풀이, 떨어져야 할 느린 풀이, 함정 오답, 대체 풀이를 따로. "Make sure that your hard problem with cool O(N*log(N)) solution could not be solved by stupid O(N^2) approach with bit optimization." "Tests which will reject all your 'wrong' solutions." — https://codeforces.com/blog/entry/12642
16. **준비 순서 (dario2994).** 제한까지 지문 확정 → checker·validator·단순 generator → 정해·단순 풀이 → TL·정당성 → 어려운 테스트 generator("this is the worst part"). 에디토리얼을 꼼꼼히 쓰는 것이 정당성을 확인하는 유일한 방법이었음. 자기 문제를 검색해 잘 알려진 문제면 버림 — https://codeforces.com/blog/entry/85424
17. **anti-hash.** "I've seen a lot of people on Codeforces get hacked or fail system tests when using these" — https://codeforces.com/blog/entry/62393

## 3. LLM으로 테스트·문제를 생성한 연구

18. **AlphaCode / CodeContests.** 기존 데이터셋의 false positive(틀린 코드 통과) 30–60%, CodeContests 4%(느리지만 맞는 코드까지 합치면 46%). 변형 입력은 "verified by running 30 correct solutions on them" — https://ar5iv.labs.arxiv.org/html/2203.07814
19. **HardTests (NeurIPS 2025).** "a well-disguised wrong solution may only be detected by carefully human-written edge cases". 입력은 LLM이 직접 쓰지 않고 LLM이 쓴 프로그램으로 생성. 소형/랜덤/해킹 입력(후보 오답을 정하고 그걸 떨어뜨리는 generator). LLM이 쓴 validator로 거름. 출력은 여러 정답 풀이가 일치할 때만 채택. TACO 어려운 문제 FP 90% 이상, APPS는 통과 프로그램의 60%가 실제 오답 — https://arxiv.org/html/2505.24098
20. **HardTests 한계.** validator가 놓치는 제약이 있음. 조건을 만족할 때까지 도는 while 루프식 생성 금지(구조를 직접 구성). "for some problems, large-scale random data is not enough". 답이 여러 개면 special judge 필요. 테스트 생성 성공률 81.9% — 같은 출처
21. **CodeContests+ (EMNLP Findings 2025).** generator: testlib, 인자 해시 시드, 작은 것부터 큰 것·특수 케이스까지 약 20개 명령. validator: 어긴 제약과 줄 번호 보고, 예제가 통과 못 하면 validator를 고침. 테스트 품질 = 정답 통과율(TPR)과 오답 탈락율(TNR). 원본 CodeContests는 테스트의 67%만 validator 통과, 4,000개 이상 문제에서 정답 거의 다 탈락, 다중 답 문제에 checker 없음 — https://arxiv.org/html/2506.05817
22. **TestCase-Eval.** 특정 오답을 떨어뜨리는 테스트 생성 비율: Qwen3-32B 43.8%, GPT-4.1 36.5%, 사람 전문가 93.3%. 커버리지는 사람과 비슷. TLE 유형 오류 노출률 21.2%로 특히 약함 — https://arxiv.org/html/2506.12278v1
23. **AutoCode (ICLR 2026).** validator: 유효 입력 10개 + near-valid 오류 입력 30개로 후보 3개 중 선택. checker: 시나리오 40개로 후보 3개 평가. generator: 작은 입력 전수, 랜덤·극값(overflow·정밀도·해시 충돌), TLE 유도. 새 문제는 정해와 brute를 작은 입력 전체에 교차 검증 → 문제 27% 걸러짐, 정해 정답률 86%→94%. **문제 품질 판단에서 LLM(o3)과 사람의 상관 0.07, 사람끼리 0.71 → 품질 판단을 LLM에 맡기면 안 됨.** 논문 내 수치가 곳곳에서 다름 — https://arxiv.org/html/2510.12803v1
