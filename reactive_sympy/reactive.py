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

    def is_known_value(self):
        for v in self.value:
            if not isinstance(v, sympy.Expr):
                return True

        return False

    @value.setter
    def value(self, v: any):
        if not isinstance(v, list):
            v = [v]
        self._reactive_value.extend(v)
        self._reactive_value = list(set(self._reactive_value))
        self._react()

    def _react(self):
        for v in self.value:
            rest = [o for o in self.value if o is not v and isinstance(o, sympy.Expr)]
            if len(rest) == 0:
                continue

            for r in rest:
                for free in r.free_symbols:
                    if free.is_known_value():
                        continue

                    free.value = sympy.solve(eq(r, v), free)

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
