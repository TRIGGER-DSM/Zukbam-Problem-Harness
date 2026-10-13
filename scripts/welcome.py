#!/usr/bin/env python3
"""세션을 시작하면 사용자에게 할 수 있는 일과 필요한 것을 보여 주는 SessionStart 훅 (.claude/settings.json에 등록).

systemMessage는 사용자 화면에 그대로 보이고, additionalContext는 Claude에게 전해진다.
진행 중인 문제(problems/*/state.md의 stage가 done이 아닌 것)가 있으면 "이어서 하기"에 함께 보여 준다.
모델 설정(harness.local.json)이 없으면 먼저 주로 쓸 모델을 정하자고 안내하고, 있으면 현재 설정을 보여 준다.
AI를 부르지 않으므로 토큰을 쓰지 않는다.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CONFIG = ROOT / "harness.local.json"
FIRST = """처음 쓰시는군요! 시작하기 전에 주로 쓸 모델부터 정할게요. 무엇을 요청하시든 먼저 물어볼게요.
  (Pro 요금제면 Sonnet + 보조 Haiku를 추천해요. 토큰을 가장 아낄 수 있어요.)

"""
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
{model}번호와 필요한 것을 편하게 말씀해 주세요. 예: "1번, DP 충전기 실버 3" """


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
    if CONFIG.is_file():
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
        model = (f"모델: 메인 {cfg.get('main_model', '?')}, 보조 에이전트 {cfg.get('helper_model', '?')} "
                 "(바꾸려면 \"모델 바꿔줘\")\n\n")
        first = ""
    else:
        model, first = "", FIRST
    menu = first + MENU.format(resume=resume, model=model)
    context = ("사용자에게 아래 메뉴를 이미 보여 줬다. 사용자가 번호나 짧은 말로 답하면 그 일로 보고 "
               "test-problem-maker-start 스킬을 부른다. 필요한 것이 빠졌으면 빠진 것만 묻는다.")
    if first:
        context += " harness.local.json이 없으므로 무엇을 요청받든 start 스킬의 0절(모델 정하기)부터 한다."
    context += "\n\n" + menu
    print(json.dumps({"systemMessage": menu,
                      "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
