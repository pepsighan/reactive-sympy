from reactive_sympy.reactive import eq, reactive_symbol

# define the symbols
x1, x2, y, k, l, ans = reactive_symbol("x1 x2 y k l ans")

# define the parabola equation
eq(y, k * x1**2 - 2 * k * x1 + l)
eq(y, k * x2**2 - 2 * k * x2 + l)

# the parabola intersects the line y = 4 at two points A and B
# so we substitute y = 4 into the parabola equation
eq(y, 4)
eq(x1 - x2, 6)

eq(ans, x1**2 + y**2 + x2**2 + y**2)

print(x1)
print(x2)
print(y)
print(k)
print(l)
print(ans)
