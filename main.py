from reactive_sympy.reactive import eq, reactive_symbol

x, y = reactive_symbol("x y")
eq(y, x + 4)

print(y)
print(x)

print("------" * 20)
x.value = 3

print(y)
print(x)
