// 모든 부분집합을 확인한다 (N이 작을 때만)
#include <algorithm>
#include <cstdio>
#include <utility>
#include <vector>
int main() {
    int n;
    scanf("%d", &n);
    std::vector<std::pair<int, int>> v(n);
    for (auto& [s, e] : v) scanf("%d %d", &s, &e);
    int best = 0;
    for (int mask = 0; mask < (1 << n); mask++) {
        std::vector<std::pair<int, int>> chosen;
        for (int i = 0; i < n; i++)
            if (mask >> i & 1) chosen.push_back(v[i]);
        std::sort(chosen.begin(), chosen.end());
        bool ok = true;
        for (size_t i = 1; i < chosen.size(); i++)
            if (chosen[i].first < chosen[i - 1].second) ok = false;
        if (ok) best = std::max(best, (int)chosen.size());
    }
    printf("%d\n", best);
}
