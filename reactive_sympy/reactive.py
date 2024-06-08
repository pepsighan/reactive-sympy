import sympy


def is_known_value(v: any):
    if isinstance(v, (int, float, complex)):
        return True

    try:
        p = v.is_number
        return p
    except AttributeError:
        return False


def resolve_expression(ex: any):
    if is_known_value(ex):
        return [ex]

    expressions = [ex]
    for sym in ex.free_symbols:
        ex_len = len(expressions)
        for sol in sym.solutions:
            for ex in expressions[:ex_len]:
                expressions.append(sympy.simplify(ex.subs(sym, sol)))

    return list(set(expressions))


class ReactiveSymbol(sympy.Symbol):
    _reactive_values: list[any]

    def __new__(cls, name, **assumptions):
        val = super().__new__(cls, name, **assumptions)
        val._reactive_values = []
        return val

    @property
    def known_values(self):
        return [v for v in self._reactive_values if is_known_value(v)]

    @property
    def solutions(self):
        known = self.known_values
        if len(known) > 0:
            return known

        return self._reactive_values

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

        vars_used = set(
            [
                s
                for r in self._reactive_values
                if not is_known_value(r)
                for s in r.free_symbols
            ]
        )
        filtered_v = [
            it
            for it in v
            if is_known_value(it)
            or not all([sym in vars_used for sym in it.free_symbols])
        ]

        self._reactive_values.extend(filtered_v)
        self._reactive_values = list(set(self._reactive_values))
        after_len = len(self._reactive_values)

        if after_len != prev_len:
            self._react()

    def _react(self):
        for v in self._reactive_values:
            for r in self._reactive_values:
                if is_known_value(r):
                    continue

                for free in r.free_symbols:
                    if len(free.known_values) > 0:
                        continue

                    eq(r, v)

    def __str__(self):
        if self._reactive_values is None:
            return self.name

        return f"{self.name} = {self.solutions}"


def reactive_symbol(names: str) -> list[ReactiveSymbol]:
    return list(sympy.symbols(names, cls=ReactiveSymbol))


def eq(lhs, rhs) -> None:
    lhses = resolve_expression(lhs)
    rhses = resolve_expression(rhs)

    for lhs in lhses:
        for rhs in rhses:
            if lhs == rhs:
                continue

            expr = sympy.Eq(lhs, rhs, evaluate=False)
            for sym in expr.free_symbols:
                solutions = sympy.solve(expr, sym)
                sym._add_values(solutions)
