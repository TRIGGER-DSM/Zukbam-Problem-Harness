// DFS로 처음 찾은 경로의 길이를 출력한다 (최단이 아닐 수 있음)
#include <cstdio>
#include <stack>
#include <string>
#include <vector>
int main() {
    int n, m;
    scanf("%d %d", &n, &m);
    std::vector<std::string> g(n);
    static char buf[1005];
    for (auto& row : g) scanf("%s", buf), row = buf;
    std::vector<int> dist(n * m, -1);
    std::stack<int> st;
    dist[0] = 0;
    st.push(0);
    const int dr[] = {0, 1, 0, -1}, dc[] = {1, 0, -1, 0};
    while (!st.empty()) {
        int cur = st.top(); st.pop();
        int r = cur / m, c = cur % m;
        for (int d = 0; d < 4; d++) {
            int nr = r + dr[d], nc = c + dc[d];
            if (nr < 0 || nr >= n || nc < 0 || nc >= m || g[nr][nc] == '#') continue;
            if (dist[nr * m + nc] != -1) continue;
            dist[nr * m + nc] = dist[cur] + 1;
            st.push(nr * m + nc);
        }
    }
    printf("%d\n", dist[n * m - 1]);
}
