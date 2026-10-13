# 풀이 근거

## 핵심 아이디어
(1, 1)에서 BFS를 하면 각 칸까지의 최소 이동 횟수를 구할 수 있다.

## 왜 맞는가
모든 이동의 비용이 1이므로, BFS는 거리 k인 칸을 모두 방문한 뒤에 거리 k+1인 칸을 방문한다. 그래서 칸을 처음 방문할 때 매긴 거리가 최소 거리이다. 끝까지 방문하지 못하면 도착할 수 없으므로 -1이다.

## 시간·공간 복잡도
O(NM) 시간과 공간.

## 의도적으로 떨어뜨리는 풀이
| 파일 | 기대 판정 | 무엇이 틀렸나 | 떨어뜨리는 TC |
|---|---|---|---|
| wrong_answer/no-minus-one.cpp | 오답 | 도착 불가를 처리하지 않음 | 예제 2, `blocked` 모드 |
| wrong_answer/diagonal.cpp | 오답 | 대각선 이동 허용 | 예제 2, `corner` 모드 |
| wrong_answer/dfs-first-path.cpp | 오답 | DFS로 처음 찾은 경로 | `open` 모드 1000×1000 (`detour` 모드는 이 구현을 잡지 못함) |
| time_limit_exceeded/backtracking.cpp | 시간 초과 | 모든 경로 탐색 | `open` 모드 1000×1000 |
