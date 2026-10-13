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
        for (int i = l; i <= r; i++) s += a[i];
        printf("%lld\n", s);
    }
}
