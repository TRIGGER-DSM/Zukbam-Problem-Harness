from vlib import Reader

r = Reader()
n = r.read_int(1, 200_000, "N")
r.read_eoln()
for _ in range(n):
    s = r.read_int(0, 10**9, "s_i")
    r.read_space()
    e = r.read_int(0, 10**9, "e_i")
    r.ensure(s < e, f"s_i={s} >= e_i={e}")
    r.read_eoln()
r.finish()
