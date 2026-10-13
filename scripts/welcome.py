#!/usr/bin/env python3
"""세션을 시작하면 사용자에게 할 수 있는 일과 필요한 것을 보여 주는 SessionStart 훅 (.claude/settings.json에 등록).

systemMessage는 사용자 화면에 그대로 보이고, additionalContext는 Claude에게 전해진다.
진행 중인 문제(problems/*/state.md의 stage가 done이 아닌 것)가 있으면 "이어서 하기"에 함께 보여 준다.
AI를 부르지 않으므로 토큰을 쓰지 않는다.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MENU = """안녕하세요! Zukbam 문제 하네스예요. 무엇을 도와드릴까요?

  1. 새 문제 만들기
     필요한 것: 풀이 방식(예: DP, 그리디), 난이도(예: 실버 3), 키워드(예: 충전기, 없으면 알아서)
  2. 지문 검토 + 테스트케이스 만들기
     필요한 것: 지문과 예제 (파일 경로를 알려 주거나 대화창에 붙여넣기)
  3. 지문 검토만
     필요한 것: 지문과 예제
  4. 가지고 있는 테스트케이스 검증
     필요한 것: 지문, 예제, 테스트케이스 폴더 (1.in·1.out처럼 번호 짝)
{resume}
번호와 필요한 것을 편하게 말씀해 주세요. 예: "1번, DP 충전기 실버 3" """


def unfinished():
    out = []
    for state in sorted(ROOT.glob("problems/*/state.md")):
        fields = dict(line.split(":", 1) for line in state.read_text(encoding="utf-8").splitlines() if ":" in line)
        stage = fields.get("stage", "").strip()
        if stage and stage != "done":
            out.append(f"{state.parent.name} (단계: {stage})")
    return out


def main():
    items = unfinished()
    resume = ""
    if items:
        resume = "  5. 이어서 하기\n" + "".join(f"     - {name}\n" for name in items)
    menu = MENU.format(resume=resume)
    context = ("사용자에게 아래 메뉴를 이미 보여 줬다. 사용자가 번호나 짧은 말로 답하면 그 일로 보고 "
               "test-problem-maker-start 스킬을 부른다. 필요한 것이 빠졌으면 빠진 것만 묻는다.\n\n" + menu)
    print(json.dumps({"systemMessage": menu,
                      "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
