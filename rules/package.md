# 문제 패키지 규약

모든 스킬은 문제 폴더를 이 규약대로 만들고 읽는다. 템플릿은 `templates/problem/`.

## 구조

```
problems/<슬러그>/
├─ problem.md                지문 (설명 / 입력 / 출력 / 제한)
├─ meta.json                 제목, 풀이 방식, 키워드, 난이도, 시간·메모리 제한, 시작 모드
├─ examples/                 지문에 보이는 예제          N.in / N.out
├─ tests/                    채점용 숨은 TC              N.in / N.out
├─ invalid/                  validator가 거부해야 하는 입력  <이유>.in (예: n-too-large.in)
├─ sol/
│  ├─ README.md              풀이 근거: 왜 맞는가, 복잡도, 떨어뜨리는 풀이 표
│  ├─ main.cpp               주 정답. .out은 이것을 실행해 만든다
│  ├─ main.py                Python 정답 (시간 제한 확인용)
│  ├─ brute.cpp              지문을 그대로 따르는 brute-force (blind-solver가 씀)
│  ├─ blind-2.cpp            (지문 검토 때) 두 번째 blind-solver의 풀이. verdicts.py가 돌리지 않음
│  ├─ accepted/              그 밖의 정답 (독립적으로 쓴 두 번째 정답 등)
│  ├─ wrong_answer/          오답이 나야 하는 풀이 (wrong-solver 에이전트가 씀. mutant-*.cpp는 변이 테스트가 찾은 것)
│  ├─ time_limit_exceeded/   시간 초과가 나야 하는 풀이 (최대한 최적화한 버전)
│  └─ runtime_error/         런타임 에러가 나야 하는 풀이
├─ gen/
│  ├─ gen.py                 입력 생성기 (명령줄 인자로 시드를 정해 재현 가능)
│  └─ tests.txt              각 TC를 만든 생성 명령
├─ validator.py              입력 검사 (validator-writer 에이전트가 쓴다. generator와 다른 쪽)
├─ checker.py                (선택) 정답이 여러 개인 문제만
├─ state.md                  진행 상태
└─ report.md                 스크립트 판정 결과 + 사람이 검토할 근거
```

## 기대 판정

| 위치 | 허용 | 필수 (TC 중 하나 이상) |
|---|---|---|
| `main.cpp`, `main.py`, `accepted/` | 통과 | — |
| `wrong_answer/` | 통과, 오답 | 오답 |
| `time_limit_exceeded/` | 통과, 시간 초과 | 시간 초과 |
| `runtime_error/` | 통과, 런타임 에러 | 런타임 에러 |
| `brute.cpp` | 통과, 시간 초과, 런타임 에러 | — (작은 입력 대조용) |

## 시간 제한

- T_ac = 정답(`main.cpp`, `main.py`, `accepted/`)이 TC 전체에서 낸 가장 느린 시간
- T_tle = `time_limit_exceeded/` 풀이들이 각자 TC 전체에서 낸 가장 느린 시간 중 가장 빠른 것
- **T_ac × 2 ≤ 시간 제한**, **시간 제한 × 1.5 ≤ T_tle**
- 만족하는 값이 없으면 입력 크기를 키워 본다. 그래도 없으면 출제자에게 [질문]

## validator 입출력

- 실행: `python3 validator.py < X.in`
- 공백, 줄바꿈, 선행 0, 파일 끝까지 엄격하게 검사한다. 모든 줄은 `\n`으로 끝난다
- 통과: 종료 코드 0. 지문의 변수마다 실제로 나온 범위를 한 줄씩 출력한다
  `범위: <변수> <최소> <최대>`
- 실패: 종료 코드 **43**. 첫 위반을 출력한다. 그 밖의 종료 코드(예외로 죽으면 1)는 validator 오류로 본다
  `제약 위반: <설명> (줄 <n>)`
- 변수 이름은 지문과 같게 쓴다
- `scripts/vlib.py`의 `Reader`로 쓴다 (스크립트가 PYTHONPATH에 넣어 준다). 공백·줄바꿈 검사와 위 출력 형식을 맡아 준다

## checker 입출력

- 실행: `python3 checker.py <입력> <참가자 출력> <정답 출력>`
- 정답이면 종료 코드 0, 오답이면 **43**. 그 밖의 종료 코드는 checker 오류로 본다 (Python은 예외로 죽어도 1이라 1은 쓰지 않는다)
- 참가자 값은 전부 범위 검사한다. 이상한 출력(빈 출력, -1, 아주 큰 수, NaN)에 죽지 않는다
