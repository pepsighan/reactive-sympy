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

    def _sort_values(self):
        self._values = sorted(
            list(set(self._values)),
            key=lambda x: 0 if is_known_value(x) else len(x.free_symbols),
        )

    def _add_values(self, v: list[any]):
        if len(v) == 0:
            return

        self._values.extend([sympy.simplify(it) for it in v])
        self._sort_values()

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

        # print({sym.name: sym.solutions for sym in self._all_symbols})

    def expr_in_terms(self, lhs: any, rhs: any, term: any) -> any:
        expr = sympy.Eq(lhs, rhs)
        val = sympy.solve(expr, term)
        if isinstance(val, bool):
            return None
        return [sympy.simplify(s) for s in val]

    def solve(self):
        while True:
            combinations = []
            for sym in self._all_symbols:
                other_symbols = [s for s in self._all_symbols if s is not sym]
                oth_values = [
                    self.expr_in_terms(oth_sym, oth_expr, sym)
                    for oth_sym in other_symbols
                    for oth_expr in oth_sym.solutions
                    if not is_known_value(oth_expr) and sym in oth_expr.free_symbols
                ]
                oth_values = [vals for vals in oth_values if vals is not None]
                oth_values = [v for vals in oth_values for v in vals]
                sym_values = sym.solutions

                for oth_val in oth_values:
                    for sym_val in sym_values:
                        combinations.append((oth_val, sym_val))

            combinations = sorted(
                combinations,
                key=lambda x: sympy.count_ops(x[0]) + sympy.count_ops(x[1]),
            )
            for lhs, rhs in combinations:
                print(
                    lhs,
                    "=",
                    rhs,
                    ";;",
                    sympy.count_ops(lhs),
                    sympy.count_ops(rhs),
                )
                self.eq(sym_val, oth_val)

            all_solved = all([len(s.known_values) > 0 for s in self._all_symbols])
            if all_solved:
                break


def is_known_value(v: any):
    if isinstance(v, (int, float, complex)):
        return True

    try:
        p = v.is_number
        return p
    except AttributeError:
        return False


def value_contains_previous_symbols(
    haystack: any, search: list[ReactiveSymbol]
) -> bool:
    if is_known_value(haystack):
        return False

    for free_sym in haystack.free_symbols:
        for s in search:
            if s is free_sym:
                return True

    return False
