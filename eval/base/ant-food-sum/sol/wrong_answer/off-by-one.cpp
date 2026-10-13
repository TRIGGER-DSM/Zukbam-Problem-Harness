// l번 칸을 빼먹는다 (pre[r] - pre[l])
#include <cstdio>
#include <vector>
int main() {
    int n, q;
    scanf("%d %d", &n, &q);
    std::vector<long long> pre(n + 1, 0);
    for (int i = 1; i <= n; i++) {
        long long a;
        scanf("%lld", &a);
        pre[i] = pre[i - 1] + a;
    }
    while (q--) {
        int l, r;
        scanf("%d %d", &l, &r);
        printf("%lld\n", pre[r] - pre[l]);
    }
}
