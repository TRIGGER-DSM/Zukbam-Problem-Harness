// 산책마다 직접 더한다: O(NQ). 최대한 빠르게 쓴 버전
#pragma GCC optimize("O3,unroll-loops")
#include <cstdio>
#include <vector>
int main() {
    int n, q;
    scanf("%d %d", &n, &q);
    std::vector<long long> a(n + 1);
    for (int i = 1; i <= n; i++) scanf("%lld", &a[i]);
    while (q--) {
        int l, r;
        scanf("%d %d", &l, &r);
        long long s = 0;
        const long long* p = a.data();
        for (int i = l; i <= r; i++) s += p[i];
        printf("%lld\n", s);
    }
}
