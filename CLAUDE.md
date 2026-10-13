# 코딩테스트 문제 harness

이 폴더에서는 백준식(stdin/stdout) 코딩테스트 문제를 만들거나 검증한다.

사용자에게 하는 보고와 질문, 문제 폴더의 문서는 모두 한국어로 쓴다.

사용자가 문제 생성, 지문 검토, 테스트케이스 생성·검증을 요청하면 **`test-problem-maker-start` 스킬을 호출한다.** 다른 스킬을 직접 부르지 않는다.

보조 에이전트(`.claude/agents/`)를 부를 때는 `harness.local.json`의 `helper_model`을 Agent 도구의 `model`로 준다 (`same`이거나 파일이 없으면 주지 않는다). 난이도 신호용 Haiku 호출은 그대로 Haiku다.

`scripts/`는 스킬에 적힌 명령 그대로 쓴다. 옵션이나 출력 문구가 궁금하면 소스 전체가 아니라 맨 위 설명(docstring)만 읽는다. 다음 단계 스킬의 SKILL.md는 미리 읽지 않는다 (호출하면 실린다).

- 원칙: `rules/principles.md` (모든 작업 전에 읽는다)
- 문제 폴더 형식: `rules/package.md`
- 문제 생성 기준(1번): `rules/generate.md`
- 결정 기록: `rules/decisions.md`
- harness 자체를 고칠 때: `DEVELOPMENT.md`
- 설계 배경: `docs/spec.md`
