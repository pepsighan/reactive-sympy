import sympy as sp

from reactive_sympy.reactive import reactive_symbol

x, y = reactive_symbol("x y")

sp.Eq(y, x + 4)

print(y)
print(x)

print("------" * 20)
x.value = 3

print(y)
print(x)
