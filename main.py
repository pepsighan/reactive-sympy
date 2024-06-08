from reactive_sympy.reactive import eq, reactive_symbol

x, y = reactive_symbol("x y")
z, a = reactive_symbol("z a")
eq(y, x + 4)

print(y)
print(x)
print(z)
print(a)

print("------" * 20)
x.value = 3


eq(z + y, a + x)

print(y)
print(x)
print(z)
print(a)
