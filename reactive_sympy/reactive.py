import sympy


class ReactiveSymbol(sympy.Symbol):
    _values: list[any]

    def __new__(cls, name, **assumptions):
        val = super().__new__(cls, name, **assumptions)
        val._values = []
        return val

    def _add_values(self, values: list[any]):
        if len(values) == 0:
            return

        for s_val in self._values:
            if values == s_val:
                return

        self._values.append(values)

    def _is_resolved(self):
        return len(self.solutions()) > 0

    def solutions(self):
        return [vals for vals in self._values if all([is_known_value(v) for v in vals])]

    def solutions_or_values(self):
        sols = self.solutions()
        if len(sols) > 0:
            return sols
        return self._values


class ReactiveSympy:
    _all_symbols: set[ReactiveSymbol]
    _symbol_links: dict[ReactiveSymbol, list[ReactiveSymbol]]

    def __init__(self) -> None:
        self._all_symbols = set([])
        self._symbol_links = {}

    def symbols(self, names: str):
        symbs = sympy.symbols(names, cls=ReactiveSymbol)
        if isinstance(symbs, tuple):
            self._all_symbols = self._all_symbols.union(symbs)
            return symbs
        else:
            self._all_symbols = self._all_symbols.union([symbs])
            return (symbs,)

    def link_symbol(self, symbol: ReactiveSymbol, vars: list[ReactiveSymbol]):
        self._symbol_links[symbol] = vars

    def eq(self, lhs: any, rhs: any) -> None:
        self._internal_eq(lhs, rhs)

    def _internal_eq(self, lhs: any, rhs: any) -> None:
        expr = sympy.Eq(lhs, rhs)

        for sym in expr.free_symbols:
            if sym not in self._all_symbols:
                continue

            if sym._is_resolved():
                continue

            solutions = sympy.solve(expr, sym)
            solutions = [sympy.simplify(s) for s in solutions]
            sym._add_values(solutions)

            link = self._symbol_links.get(sym, None)
            if link is not None:
                if len(link) != len(solutions):
                    print("no link here")

                if len(link) == len(solutions):
                    for li, s in zip(link, solutions):
                        li._add_values([s])

        print({s.name: s._values for s in self._all_symbols}, end="\n\n")

    def solve(self):
        print("solving...")
        for symbol in self._all_symbols:
            for lhses in symbol._values:
                for lhs in lhses:
                    for rhses in symbol._values:
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
