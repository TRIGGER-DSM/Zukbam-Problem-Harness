#!/usr/bin/env python3
"""실제 문제 메타데이터(solved.ac)로 풀이 방식·티어에 맞는 참고 정보를 보여 준다. 문제 생성(1번)에서 쓴다.

사용:
  python3 scripts/refs.py <풀이 방식> <티어> [--data refs/solvedac.json]
      예: refs.py dp g3 / refs.py "다이나믹 프로그래밍" "골드 3" / refs.py 누적합 실버3
  python3 scripts/refs.py build          refs/solvedac.json을 새로 받는다 (네트워크, 약 10분)

refs/solvedac.json에는 티어가 매겨진 문제 전부(브론즈 5~다이아 1, 약 3만 개)의
번호·제목·티어·태그·푼 사람 수만 있다. 지문은 받지 않는다 (백준은 2026년 서비스 종료, 지문은 저작물).
풀이 방식은 solved.ac 태그 키, 한국어 이름, 별칭 중 무엇으로 줘도 된다 (띄어쓰기·대소문자 무시).

출력 줄(고정 문구):
  태그: <키> (<한국어 이름>)
  티어: <티어>
  표본: 이 티어 <n>문제 중 <k>문제
  함께 붙는 태그: <이름> <개수>, ...
  대표 문제: <번호> <제목> [<태그들>] (푼 사람 <n>)
  티어별 분포: <티어> <개수>, ...
  태그를 찾지 못함: <입력> (비슷한 태그: ...)
  티어를 읽지 못함: <입력>
  저장: refs/solvedac.json (<n>문제)
종료 코드: 찾으면 0, 태그·티어를 못 읽거나 표본에 없으면 1
"""
import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "refs" / "solvedac.json"
API = "https://solved.ac/api/v3/search/problem"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
RETRY = 5
SHOW = 5
TIER_NAMES = {"b": "브론즈", "s": "실버", "g": "골드", "p": "플래티넘", "d": "다이아"}
KO_TO_LETTER = {v: k for k, v in TIER_NAMES.items()} | {"다이아몬드": "d", "플레": "p", "플래": "p"}


def tier_name(level: int):
    letter = "bsgpd"[(level - 1) // 5]
    return f"{TIER_NAMES[letter]} {5 - (level - 1) % 5}"


def parse_tier(text: str):
    t = text.replace(" ", "").lower()
    m = re.fullmatch(r"([bsgpd])([1-5])", t)
    if not m:
        for ko, letter in sorted(KO_TO_LETTER.items(), key=lambda x: -len(x[0])):
            m2 = re.fullmatch(re.escape(ko) + r"([1-5])", t)
            if m2:
                return "bsgpd".index(letter) * 5 + 6 - int(m2.group(1))
        return None
    return "bsgpd".index(m.group(1)) * 5 + 6 - int(m.group(2))


def norm(s: str):
    return re.sub(r"[\s_\-]", "", s.lower())


def find_tag(tags: dict, text: str):
    q = norm(text)
    for key, info in tags.items():
        if q in {norm(key), norm(info["ko"]), *map(norm, info["aliases"])}:
            return key
    return None


def fetch(level: int, page: int):
    letter = "bsgpd"[(level - 1) // 5]
    query = f"tier:{letter}{5 - (level - 1) % 5}"
    url = f"{API}?{urllib.parse.urlencode({'query': query, 'sort': 'solved', 'direction': 'desc', 'page': page})}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    for attempt in range(RETRY):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except OSError:  # 429·일시 오류: 기다렸다 다시
            time.sleep(10 * (attempt + 1))
    raise SystemExit(f"받기 실패: {query} page {page}")


def build():
    problems, tags = [], {}
    for level in range(1, 26):
        page = 1
        while True:
            items = fetch(level, page)["items"]
            if not items:
                break
            page += 1
            for p in items:
                problems.append({"id": p["problemId"], "title": p["titleKo"], "level": p["level"],
                                 "solved": p["acceptedUserCount"], "tags": [t["key"] for t in p["tags"]]})
                for t in p["tags"]:
                    ko = next((d["name"] for d in t["displayNames"] if d["language"] == "ko"), t["key"])
                    tags[t["key"]] = {"ko": ko, "aliases": [a["alias"] for a in t.get("aliases", [])]}
            time.sleep(0.7)
    DATA.parent.mkdir(exist_ok=True)
    DATA.write_text(json.dumps({"fetched": date.today().isoformat(), "problems": problems, "tags": tags},
                               ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"저장: refs/solvedac.json ({len(problems)}문제)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("method")
    ap.add_argument("tier", nargs="?")
    ap.add_argument("--data", default=str(DATA))
    args = ap.parse_args()
    if args.method == "build":
        build()
        return
    data = json.loads(Path(args.data).read_text(encoding="utf-8"))
    tags = data["tags"]
    key = find_tag(tags, args.method)
    if key is None:
        q = norm(args.method)
        near = [f"{k}({v['ko']})" for k, v in tags.items() if q[:2] and (q[:2] in norm(k) or q[:2] in norm(v["ko"]))]
        print(f"태그를 찾지 못함: {args.method} (비슷한 태그: {', '.join(near[:8]) or '없음'})")
        sys.exit(1)
    level = parse_tier(args.tier or "")
    if level is None:
        print(f"티어를 읽지 못함: {args.tier}")
        sys.exit(1)
    name = lambda k: tags.get(k, {}).get("ko", k)

    print(f"태그: {key} ({name(key)})")
    print(f"티어: {tier_name(level)}")
    at_tier = [p for p in data["problems"] if p["level"] == level]
    hits = sorted((p for p in at_tier if key in p["tags"]), key=lambda p: -p["solved"])
    print(f"표본: 이 티어 {len(at_tier)}문제 중 {len(hits)}문제")
    co = Counter(t for p in hits for t in p["tags"] if t != key)
    if co:
        print("함께 붙는 태그: " + ", ".join(f"{name(t)} {c}" for t, c in co.most_common(8)))
    for p in hits[:SHOW]:
        print(f"대표 문제: {p['id']} {p['title']} [{', '.join(name(t) for t in p['tags'])}] (푼 사람 {p['solved']})")
    dist = Counter(p["level"] for p in data["problems"] if key in p["tags"])
    print("티어별 분포: " + ", ".join(f"{tier_name(lv)} {dist[lv]}" for lv in sorted(dist)))
    sys.exit(0 if hits else 1)


if __name__ == "__main__":
    main()
