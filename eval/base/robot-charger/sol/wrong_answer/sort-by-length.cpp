// 짧은 신청부터 고른다: 짧지만 두 신청에 걸치는 경우에 틀린다
#include <algorithm>
#include <cstdio>
#include <set>
#include <utility>
#include <vector>
int main() {
    int n;
    scanf("%d", &n);
    std::vector<std::pair<int, int>> v(n);
    for (auto& [s, e] : v) scanf("%d %d", &s, &e);
    std::sort(v.begin(), v.end(), [](auto a, auto b) { return a.second - a.first < b.second - b.first; });
    std::set<std::pair<int, int>> taken;  // (시작, 끝)
    int cnt = 0;
    for (auto [s, e] : v) {
        auto it = taken.lower_bound({s, -1});
        if (it != taken.end() && it->first < e) continue;
        if (it != taken.begin() && std::prev(it)->second > s) continue;
        taken.insert({s, e});
        cnt++;
    }
    printf("%d\n", cnt);
}
