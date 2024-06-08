import sympy


class ReactiveSymbol(sympy.Symbol):
    _reactive_values: list[any]

    def __new__(cls, name, **assumptions):
        val = super().__new__(cls, name, **assumptions)
        val._reactive_values = []
        return val

    @property
    def known_values(self):
        return [
            v
            for v in self._reactive_values
            if not isinstance(v, sympy.Expr)
            or (isinstance(v, sympy.Expr) and len(v.free_symbols) == 0)
        ]

    @property
    def _values(self):
        return self._reactive_values

    @_values.setter
    def value(self, v: any):
        v = [v]
        self._add_values(v)

    def _add_values(self, v: list[any]):
        if len(v) == 0:
            return

        prev_len = len(self._reactive_values)
        self._reactive_values.extend(v)
        self._reactive_values = list(set(self._reactive_values))
        after_len = len(self._reactive_values)

        if after_len != prev_len:
            self._react()

    def _react(self):
        for v in self._reactive_values:
            rest = [
                o
                for o in self._reactive_values
                if o is not v and isinstance(o, sympy.Expr)
            ]
            if len(rest) == 0:
                continue

            for r in rest:
                for free in r.free_symbols:
                    if len(self.known_values) > 0:
                        continue

                    sols = sympy.solve(eq(r, v), free)
                    sols = [sympy.simplify(sol) for sol in sols]
                    free._add_values(sols)

    def __str__(self):
        if self._reactive_values is None:
            return self.name

        return f"{self.name} = {self.known_values}"


def reactive_symbol(names: str) -> list[ReactiveSymbol]:
    return list(sympy.symbols(names, cls=ReactiveSymbol))


def eq(lhs, rhs) -> sympy.Eq:
    expr = sympy.Eq(lhs, rhs, evaluate=False)
    for sym in expr.free_symbols:
        solutions = sympy.solve(expr, sym)
        sym._add_values(solutions)

    return expr
