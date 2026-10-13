// 누적합을 int로 저장해 합이 2^31을 넘으면 틀린다
#include <cstdio>
#include <vector>
int main() {
    int n, q;
    scanf("%d %d", &n, &q);
    std::vector<int> pre(n + 1, 0);
    for (int i = 1; i <= n; i++) {
        int a;
        scanf("%d", &a);
        pre[i] = pre[i - 1] + a;
    }
    while (q--) {
        int l, r;
        scanf("%d %d", &l, &r);
        printf("%d\n", pre[r] - pre[l - 1]);
    }
}
