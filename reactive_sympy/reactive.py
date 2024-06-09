import sympy


class ReactiveSymbol(sympy.Symbol):
    _values: list[any]
    _frozen: list[any]

    def __new__(cls, name, **assumptions):
        val = super().__new__(cls, name, **assumptions)
        val._values = []
        return val

    def _add_values(self, v: list[any]):
        if len(v) == 0:
            return

        vals = [sympy.simplify(it) for it in v]
        self._values.append(vals)


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
        self.solve()

    def solve(self):
        print("start solve")


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
