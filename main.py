from reactive_sympy.reactive import ReactiveSympy

sy = ReactiveSympy()

# define the symbols
x1, x2, y, k, l, ans = sy.symbols("x1 x2 y k l ans")

# sy.eq(x1 - y, 10)
# sy.eq(x1 + y, 20)

# define the parabola equation
sy.eq(y, k * x1**2 - 2 * k * x1 + l)
sy.eq(y, k * x2**2 - 2 * k * x2 + l)

# the parabola intersects the line y = 4 at two points A and B
# so we substitute y = 4 into the parabola equation
sy.eq(y, 4)
sy.eq(x1 - x2, 6)

sy.eq(ans, x1**2 + y**2 + x2**2 + y**2)
# sy.solve()

print(f"{x1.solutions=}")
print(f"{x2.solutions=}")
print(f"{y.solutions=}")
print(f"{k.solutions=}")
print(f"{l.solutions=}")
print(f"{ans.solutions=}")
