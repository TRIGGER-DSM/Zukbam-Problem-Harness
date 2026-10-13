// 거리 배열을 바뀌지 않을 때까지 반복해서 완화한다 (벨만-포드 방식, 작은 격자용)
#include <cstdio>
#include <string>
#include <vector>
int main() {
    int n, m;
    scanf("%d %d", &n, &m);
    std::vector<std::string> g(n);
    static char buf[1005];
    for (auto& row : g) scanf("%s", buf), row = buf;
    const int INF = 1 << 29;
    std::vector<std::vector<int>> d(n, std::vector<int>(m, INF));
    d[0][0] = 0;
    for (bool changed = true; changed;) {
        changed = false;
        for (int r = 0; r < n; r++)
            for (int c = 0; c < m; c++) {
                if (g[r][c] == '#') continue;
                int best = d[r][c];
                if (r > 0 && g[r - 1][c] == '.') best = std::min(best, d[r - 1][c] + 1);
                if (r + 1 < n && g[r + 1][c] == '.') best = std::min(best, d[r + 1][c] + 1);
                if (c > 0 && g[r][c - 1] == '.') best = std::min(best, d[r][c - 1] + 1);
                if (c + 1 < m && g[r][c + 1] == '.') best = std::min(best, d[r][c + 1] + 1);
                if (best < d[r][c]) d[r][c] = best, changed = true;
            }
    }
    printf("%d\n", d[n - 1][m - 1] >= INF ? -1 : d[n - 1][m - 1]);
}
