// 끝 시각 순으로 정렬한 뒤 dp[i] = 1 + max(dp[j] | e_j <= s_i): O(N^2)
#pragma GCC optimize("O3,unroll-loops")
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
    std::vector<int> dp(n);
    int best = 0;
    for (int i = 0; i < n; i++) {
        int m = 0;
        for (int j = 0; j < i; j++)
            if (v[j].first <= v[i].second && dp[j] > m) m = dp[j];
        dp[i] = m + 1;
        best = std::max(best, dp[i]);
    }
    printf("%d\n", best);
}
