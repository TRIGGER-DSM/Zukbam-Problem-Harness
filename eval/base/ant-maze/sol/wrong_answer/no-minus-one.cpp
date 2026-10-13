// 도착할 수 없는 경우를 처리하지 않는다 (거리 초깃값 0을 그대로 출력)
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
    std::vector<int> dist(n * m, 0);
    std::vector<char> seen(n * m, 0);
    std::queue<int> q;
    seen[0] = 1;
    q.push(0);
    const int dr[] = {1, -1, 0, 0}, dc[] = {0, 0, 1, -1};
    while (!q.empty()) {
        int cur = q.front(); q.pop();
        int r = cur / m, c = cur % m;
        for (int d = 0; d < 4; d++) {
            int nr = r + dr[d], nc = c + dc[d];
            if (nr < 0 || nr >= n || nc < 0 || nc >= m || g[nr][nc] == '#') continue;
            if (seen[nr * m + nc]) continue;
            seen[nr * m + nc] = 1;
            dist[nr * m + nc] = dist[cur] + 1;
            q.push(nr * m + nc);
        }
    }
    printf("%d\n", dist[n * m - 1]);
}
