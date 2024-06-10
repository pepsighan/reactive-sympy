from reactive_sympy.reactive import ReactiveSympy


sy = ReactiveSympy()

# define the symbols
x, x1, x2, y, k, l, ans = sy.symbols("x x1 x2 y k l ans")

# sy.eq(x1 - y, 10)
# sy.eq(x1 + y, 20)

# define the parabola equation
sy.eq(y, k * x**2 - 2 * k * x + l)
sy.set_roots(x, [x1, x2])

# the parabola intersects the line y = 4 at two points A and B
# so we substitute y = 4 into the parabola equation
sy.eq(y, 4)
sy.eq(x1 - x2, 6)

sy.eq(ans, x1**2 + y**2 + x2**2 + y**2)
sy.solve(ans)

print(f"{x._values=}")
print(f"{x1._values=}")
print(f"{x2._values=}")
print(f"{y._values=}")
print(f"{k._values=}")
print(f"{l._values=}")
print(f"{ans._values=}")
