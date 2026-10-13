// 모든 경로를 백트래킹으로 탐색한다 (지금까지 찾은 최단보다 길면 가지치기)
#pragma GCC optimize("O3")
#include <cstdio>
#include <string>
#include <vector>
int n, m, best = -1;
std::vector<std::string> g;
std::vector<char> seen;
void go(int r, int c, int len) {
    if (best != -1 && len >= best) return;
    if (r == n - 1 && c == m - 1) { best = len; return; }
    const int dr[] = {0, 1, 0, -1}, dc[] = {1, 0, -1, 0};
    for (int d = 0; d < 4; d++) {
        int nr = r + dr[d], nc = c + dc[d];
        if (nr < 0 || nr >= n || nc < 0 || nc >= m || g[nr][nc] == '#' || seen[nr * m + nc]) continue;
        seen[nr * m + nc] = 1;
        go(nr, nc, len + 1);
        seen[nr * m + nc] = 0;
    }
}
int main() {
    scanf("%d %d", &n, &m);
    g.resize(n);
    static char buf[1005];
    for (auto& row : g) scanf("%s", buf), row = buf;
    seen.assign(n * m, 0);
    seen[0] = 1;
    go(0, 0, 0);
    printf("%d\n", best);
}
