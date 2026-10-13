from vlib import Reader

r = Reader()
n = r.read_int(1, 1000, "N")
r.read_space()
m = r.read_int(1, 1000, "M")
r.read_eoln()
grid = []
for _ in range(n):
    grid.append(r.read_token(f"[.#]{{{m}}}", "격자 행"))
    r.read_eoln()
r.ensure(grid[0][0] == ".", "(1, 1)이 벽")
r.ensure(grid[n - 1][m - 1] == ".", "(N, M)이 벽")
r.finish()
