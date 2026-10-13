# 구조 결정 기록

배경과 대화 전문은 `docs/spec.md`에 있다.

## 2026-10-12

- **오프라인 실행.** 운영자가 이 폴더에서 `claude`를 실행한다. 나중에 필요하면 백엔드 기능으로 옮기고, 스크립트는 외부 프로세스로 호출해 재사용한다.
- **백준식 stdin/stdout 채점.** TC는 `N.in` / `N.out` 파일 쌍이다.
- **하나의 파이프라인.** 입력이 키워드면 1번(generate), 지문이면 2번(statement-review → testgen), 지문+TC면 3번(testcheck)에서 시작한다. 진입은 `test-problem-maker-start` 스킬 하나다.
- **판정은 결정적인 스크립트가 내린다.** AI의 자기 보고를 믿지 않기 위해서다.
- **언어.** 풀이 코드(정답, brute-force, 오답)는 C++. Python 정답(`sol/main.py`)도 둔다. 문제별 보조 코드(generator, validator, checker)와 harness 스크립트는 Python.
- **3번은 TC 자체의 오류와 TC의 약함을 둘 다 본다.** 앞의 것을 먼저 확인하지 않으면 뒤의 결과를 믿을 수 없다.
- **1번 입력.** 풀이 방식 + 키워드 + 난이도(백준 티어 표기). 제약 조건은 AI가 정하고, 풀이를 강제할 조건이 필요할 때만 지정한다. 기존 문제 변형과 여러 개 일괄 생성도 받는다.
- **시간 제한은 하나.** Python 정답은 통과하고 느린 C++ 풀이는 넘지 못하게 정한다. 언어별 추가 시간은 두지 않는다.
- **시간은 CPU 시간으로 잰다.** 벽시계 시간보다 다른 작업의 영향을 덜 받는다.
- **샌드박스는 넣지 않는다.** 걱정한 위험은 틀린 정답 코드뿐이다. 무한 루프·런타임 에러는 시간 제한과 종료 코드로 잡는다.
- **외부 전송은 넣지 않는다.** 참고 레포(portfolio-harness)의 Discord 전송 훅은 가져오지 않았다.
- **공통 스크립트는 `scripts/`에 둔다.** 처음 구조안에서는 `testcheck/scripts/`였지만 testgen도 같이 쓰므로 옮겼다.
- **스킬 이름에는 모두 `test-problem-maker-` 접두사를 붙인다.** 처음 `review`가 이미 설치된 gstack 스킬과 겹쳤다. 다른 스킬과 겹치지 않게 한다.
- **출제 과정 리서치 반영 (C1~C6).** 근거는 `docs/research/checklist.md`.
  - 풀이를 기대 판정별 폴더로 나눈다 (`sol/accepted/`, `wrong_answer/`, `time_limit_exceeded/`, `runtime_error/`). Kattis 방식으로, 폴더만 보고 기대 판정을 자동 확인하기 위해서다.
  - `invalid/`에 validator가 거부해야 할 입력을 둔다.
  - `sol/README.md`에 정답의 근거를 적는다. brute-force 대조를 통과하고도 정답이 틀린 사례(CF Round 421)가 있다.
  - 시간 제한: T_ac × 2 ≤ TL, TL × 1.5 ≤ T_tle (Kattis 기본값).
  - validator와 generator는 다른 에이전트가 쓴다 (IOI 방식).
  - validator는 통과 시 변수별 관측 범위를, 실패 시 위반과 줄 번호를 출력한다. 경계값이 실제 TC에 나왔는지 확인하기 위해서다.
- **checker와 validator의 "거부/오답" 종료 코드는 43.** Python은 예외로 죽어도 종료 코드가 1이라, 1을 쓰면 죽은 것과 판정을 구분할 수 없다 (회귀 테스트와 평가 세트에서 실제로 발견). 0과 43이 아닌 종료 코드는 그 프로그램의 오류로 보고한다.
- **validator는 `scripts/vlib.py`(testlib의 Python판)로 쓴다.** 공백·줄바꿈 검사를 문제마다 새로 짜다 생기는 실수를 막는다.
- **서브에이전트 두 개.** `test-problem-maker-blind-solver`(지문만 보고 brute-force), `test-problem-maker-validator-writer`(지문만 보고 validator). 다른 파일을 읽지 말라는 것은 지침일 뿐 도구로 막지는 못한다.
- **평가 세트는 git에 넣는다 (`eval/`).** 정상 문제 3개(누적합, 그리디, BFS)와 결함 케이스. 생성된 TC는 73MB라 넣지 않고 채점할 때 다시 만든다.
- **서브에이전트 파일 접근은 훅으로 막는다 (`scripts/agent_guard.py`, `.claude/settings.json`의 PreToolUse).** Claude Code는 서브에이전트별 경로 권한을 지원하지 않지만, 훅 입력의 `agent_type`으로 어느 에이전트인지 알 수 있다. 허용 목록 방식: blind-solver는 `problem.md`·`examples/`만 읽고 `sol/brute.cpp`·`sol/blind-2.cpp`만 쓴다. validator-writer는 거기에 `rules/package.md`·`scripts/vlib.py`를 더 읽고 `validator.py`·`invalid/`만 쓴다. harness의 `eval/`(정답이 있음)은 둘 다 못 본다. Bash는 금지 경로 조각과 넓은 탐색 명령(find, grep -r, ls -R, git)을 막는다. 보안 경계가 아니라 실수를 막는 린트다. 실제 서브에이전트로 차단을 확인했다(2026-10-12).

## 2026-10-13

- **실제 Claude 실행 결과로 고친 것.**
  - 정답 풀이 시간은 TC마다 최대 3번 재서 최솟값을 쓴다. harness 6개를 동시에 돌리자 Python 정답이 0.21초 → 0.53초로 측정되어 시간 제한을 잘못 추천했다.
  - `time_limit_ms`가 0(템플릿 값)이면 `verdicts.py`가 1000ms 기준으로 재고 추천값을 낸다. 전에는 0초로 처리해 추천을 못 했다 (실행한 Claude가 발견).
  - 평가 케이스 `maze-missing-unreachable`은 처음 버전이 결함이 아니었다(출력 절에 문장이 남아 있었다). 실행한 Claude가 "결함 없음"이라 한 것이 옳았다. 두 곳 모두 지우도록 고쳤다.
- **변이 테스트를 넣었다 (`scripts/mutate.py`).** `sol/main.cpp`를 한 글자씩 바꾼 풀이(`<`↔`<=`, `long long`→`int`, `±1` 등)가 TC를 모두 통과하는데 작은 랜덤 입력에서 brute와 다르면 TC 구멍으로 본다. 평가 세트의 개미 미로(모든 검사 통과, 오답 풀이 3개 모두 탈락)에서 방향 배열 숫자 하나가 틀린 BFS가 숨은 TC 19개를 모두 통과하는 구멍을 찾았다. AI 호출 없이 문제당 10~20초. 평가 세트의 정상 문제 검사에 넣고, 구멍을 메우기 전 상태를 케이스(`maze-mutant-direction`)로 남겼다. 한계: 작은 입력으로만 대조하므로 큰 값에서만 드러나는 실수(오버플로)는 `동등 추정`으로 나온다.
- **떨어뜨릴 풀이는 별도 에이전트가 쓴다 (`test-problem-maker-wrong-solver`).** 전에는 TC를 만드는 쪽이 오답 풀이도 써서, 놓치는 실수가 겹쳤다. 지문·예제만 보고 쓰고, TC를 만드는 쪽은 처음 `verdicts.py`를 돌리기 전까지 그 풀이를 보지 않는다. 처음 결과에서 통과한 오답 수가 TC 강도의 정직한 측정값이 된다.
- **harness는 `claude --setting-sources project,local --strict-mcp-config`로 연다 (`README.md`).** 지난 실행 8개의 기록을 보니 도구 출력은 작았고(가장 큰 것이 6천 자), 비용의 대부분은 매 요청마다 다시 읽는 기본 문맥이었다. 그중 절반 이상이 이 harness와 상관없는 전역 플러그인 스킬 목록, MCP 도구 이름, SessionStart 훅 주입이었다. 빼면 첫 요청 문맥이 3.8만 → 1.8만 토큰이 된다. 이 옵션으로도 프로젝트 스킬·에이전트·가드 훅은 그대로 동작함을 확인했다.
- **낮은 모델로도 돌아간다 (Sonnet 5.5, Haiku 5.5로 확인).** 지문 결함 케이스 5개: Opus 10/10(5개 × 2회), Sonnet 5/5, Haiku 5/5에서 결함을 찾았다. 약한 TC 3번 모드: 세 모델 모두 시작 시각 순 그리디가 통과한다는 것을 찾았다. Haiku 2번 모드 전체(로봇 충전): 만든 TC 22개에서 평가 세트의 정답은 모두 통과했고 오답·시간 초과 풀이 4개는 모두 떨어졌다. 비용은 지문 검토 1회에 Opus 약 $0.5, Sonnet 약 $0.07, Haiku 약 $0.02였다.
- **start 스킬에 "직접 검토하지 않는다"를 넣었다.** Haiku는 처음에 5개 중 3개에서 start 스킬만 부르고 문제 폴더·blind-solver·스크립트 없이 혼자 지문을 읽고 보고했다. 규칙을 넣은 뒤 같은 3개를 다시 돌리니 모두 절차를 따랐다.
- 평가할 때 주의: 실행 폴더 이름에 케이스 이름(`ambiguous-touch` 등)을 넣으면 모델이 그것을 힌트로 쓴다 (Haiku가 실제로 언급). 실행 폴더 이름은 중립적으로 짓는다.
