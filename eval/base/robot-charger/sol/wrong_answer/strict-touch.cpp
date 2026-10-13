// 끝나는 시각과 시작 시각이 같으면 안 된다고 잘못 읽었다
#include <algorithm>
#include <cstdio>
#include <utility>
#include <vector>
int main() {
    int n;
    scanf("%d", &n);
    std::vector<std::pair<int, int>> v(n);
    for (auto& [e, s] : v) scanf("%d %d", &s, &e);
    std::sort(v.begin(), v.end());
    int cnt = 0;
    long long last = -1;
    for (auto [e, s] : v)
        if (s > last) cnt++, last = e;
    printf("%d\n", cnt);
}
