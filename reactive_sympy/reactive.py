import sympy


class ReactiveSymbol(sympy.Symbol):
    _reactive_value: list[any]

    def __new__(cls, name, **assumptions):
        val = super().__new__(cls, name, **assumptions)
        val._reactive_value = []
        return val

    @property
    def value(self):
        return self._reactive_value

    @value.setter
    def value(self, v: any):
        if not isinstance(v, list):
            v = [v]
        self._reactive_value.extend(v)

    def __str__(self):
        if self._reactive_value is None:
            return self.name

        return f"{self.name} = {self.value}"


def reactive_symbol(names: str) -> list[ReactiveSymbol]:
    return list(sympy.symbols(names, cls=ReactiveSymbol))


def eq(lhs, rhs) -> sympy.Eq:
    expr = sympy.Eq(lhs, rhs, evaluate=False)
    for sym in expr.free_symbols:
        solutions = sympy.solve(expr, sym)
        sym.value = solutions

    return expr
