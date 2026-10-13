#include <algorithm>
#include <cstdio>
#include <utility>
#include <vector>
int main() {
    int n;
    scanf("%d", &n);
    std::vector<std::pair<int, int>> v(n);  // (끝, 시작)
    for (auto& [e, s] : v) scanf("%d %d", &s, &e);
    std::sort(v.begin(), v.end());
    int cnt = 0, last = 0;
    for (auto [e, s] : v)
        if (s >= last) cnt++, last = e;
    printf("%d\n", cnt);
}
