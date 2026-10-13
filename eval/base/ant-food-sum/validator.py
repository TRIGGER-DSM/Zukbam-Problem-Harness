from vlib import Reader

r = Reader()
n = r.read_int(1, 200_000, "N")
r.read_space()
q = r.read_int(1, 200_000, "Q")
r.read_eoln()
r.read_ints(n, -10**9, 10**9, "a_i")
r.read_eoln()
for _ in range(q):
    l = r.read_int(1, n, "l")
    r.read_space()
    rr = r.read_int(1, n, "r")
    r.ensure(l <= rr, f"l={l} > r={rr}")
    r.read_eoln()
r.finish()
