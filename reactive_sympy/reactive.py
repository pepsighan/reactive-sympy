import sympy


class ReactiveSymbol(sympy.Symbol):
    _values: list[any]

    def __new__(cls, name, **assumptions):
        val = super().__new__(cls, name, **assumptions)
        val._values = []
        return val

    def add_values(self, v: list[any]):
        if len(v) == 0:
            return
        self._values.append(v)

    def solutions(self):
        return [vals for vals in self._values if all([is_known_value(v) for v in vals])]


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
        self._internal_eq(lhs, rhs)
        self.solve()

    def _internal_eq(self, lhs: any, rhs: any) -> None:
        expr = sympy.Eq(lhs, rhs)
        for sym in expr.free_symbols:
            solutions = sympy.solve(expr, sym)
            sym.add_values(solutions)

    def expr_in_terms(self, lhs: any, rhs: any, term: any) -> any:
        expr = sympy.Eq(lhs, rhs)
        val = sympy.solve(expr, term)
        if isinstance(val, bool):
            return None
        return [sympy.simplify(s) for s in val]

    def solve(self):
        pass


def is_known_value(v: any):
    if isinstance(v, (int, float, complex)):
        return True

    try:
        p = v.is_number
        return p
    except AttributeError:
        return False
