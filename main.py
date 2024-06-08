import sympy as sp

from reactive_sympy.reactive import reactive_symbol

x, y = reactive_symbol("x y")

eq = sp.Eq(y, x + 4)

x.set_value(3)

print(eq)
print(y)
print(x)
