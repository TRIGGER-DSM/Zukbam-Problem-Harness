// 대각선 이동도 된다고 잘못 읽었다 (8방향 BFS)
#include <cstdio>
#include <queue>
#include <string>
#include <vector>
int main() {
    int n, m;
    scanf("%d %d", &n, &m);
    std::vector<std::string> g(n);
    static char buf[1005];
    for (auto& row : g) scanf("%s", buf), row = buf;
    std::vector<int> dist(n * m, -1);
    std::queue<int> q;
    dist[0] = 0;
    q.push(0);
    while (!q.empty()) {
        int cur = q.front(); q.pop();
        int r = cur / m, c = cur % m;
        for (int dr = -1; dr <= 1; dr++)
            for (int dc = -1; dc <= 1; dc++) {
                int nr = r + dr, nc = c + dc;
                if (nr < 0 || nr >= n || nc < 0 || nc >= m || g[nr][nc] == '#') continue;
                if (dist[nr * m + nc] != -1) continue;
                dist[nr * m + nc] = dist[cur] + 1;
                q.push(nr * m + nc);
            }
    }
    printf("%d\n", dist[n * m - 1]);
}
