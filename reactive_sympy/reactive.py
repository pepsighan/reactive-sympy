import sympy


class ReactiveSymbol(sympy.Symbol):
    _values: list[any]

    def __new__(cls, name, **assumptions):
        val = super().__new__(cls, name, **assumptions)
        val._values = []
        return val

    @property
    def known_values(self):
        return [v for v in self._values if is_known_value(v)]

    @property
    def solutions(self):
        known = self.known_values
        if len(known) > 0:
            return known

        return self._values

    @property
    def _internal_values(self):
        return self._values

    @_internal_values.setter
    def value(self, v: any):
        v = [v]
        self._add_values(v)

    def _add_values(self, v: list[any]):
        if len(v) == 0:
            return

        self._values.extend([sympy.simplify(it) for it in v])
        self._values = sorted(
            list(set(self._values)),
            key=lambda x: 0 if is_known_value(x) else len(x.free_symbols),
        )

    def __str__(self):
        return self.name


class ReactiveSympy:
    _all_symbols: list[ReactiveSymbol]

    def __init__(self) -> None:
        self._all_symbols = []

    def symbols(self, names: str):
        symbs = sympy.symbols(names, cls=ReactiveSymbol)
        if isinstance(symbs, tuple):
            self._all_symbols.extend(symbs)
            return symbs
        else:
            self._all_symbols.append(symbs)
            return (symbs,)

    def eq(self, lhs: any, rhs: any) -> None:
        expr = sympy.Eq(lhs, rhs)
        for sym in expr.free_symbols:
            solutions = sympy.solve(expr, sym)
            sym._add_values(solutions)
        print({s: s.solutions for s in self._all_symbols})

    def solve(self):
        for s in self._all_symbols:
            if len(s.known_values) > 0:
                continue

            exprs = [*s._values]

            while len(exprs) > 0:
                ex = exprs.pop(0)

                for symb in ex.free_symbols:
                    for sol in symb._values:
                        if not is_known_value(sol) and symb in sol.free_symbols:
                            continue
                        ex_copy = ex.subs(symb, sol)
                        if ex is not ex_copy:
                            self.eq(s, ex_copy)

        requires_calculation = any(
            [True for s in self._all_symbols if len(s.known_values) == 0]
        )
        if requires_calculation:
            print("calc")
            self.solve()


def is_known_value(v: any):
    if isinstance(v, (int, float, complex)):
        return True

    try:
        p = v.is_number
        return p
    except AttributeError:
        return False
