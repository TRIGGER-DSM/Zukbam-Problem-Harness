// 시작이 빠른 순으로 고른다: 길게 덮는 신청 하나에 막힌다
#include <algorithm>
#include <cstdio>
#include <utility>
#include <vector>
int main() {
    int n;
    scanf("%d", &n);
    std::vector<std::pair<int, int>> v(n);
    for (auto& [s, e] : v) scanf("%d %d", &s, &e);
    std::sort(v.begin(), v.end());
    int cnt = 0, last = 0;
    for (auto [s, e] : v)
        if (s >= last) cnt++, last = e;
    printf("%d\n", cnt);
}
