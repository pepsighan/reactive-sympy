import sympy


class ReactiveSymbol(sympy.Symbol):
    _values: list[any]

    def __new__(cls, name, **assumptions):
        val = super().__new__(cls, name, **assumptions)
        val._values = []
        return val

    def _add_values(self, v: list[any]):
        if len(v) == 0:
            return

        vals = [sympy.simplify(it) for it in v]
        self._values.append(vals)

    def _is_resolved(self):
        return any([all([is_known_value(v) for v in vals]) for vals in self._values])


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

        syms = expr.free_symbols
        all_resolved = all([s._is_resolved() for s in syms])
        if all_resolved:
            return

        for sym in expr.free_symbols:
            solutions = sympy.solve(expr, sym)
            sym._add_values(solutions)

        print({s.name: s._values for s in syms}, end="\n\n")

    def solve(self):
        print("solving...")
        for symbol in self._all_symbols:
            print("solving:", symbol)
            for i in range(len(symbol._values)):
                lhses = symbol._values[i]
                for lhs in lhses:
                    for j in range(i + 1, len(symbol._values)):
                        rhses = symbol._values[j]
                        for rhs in rhses:
                            self._internal_eq(lhs, rhs)


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
