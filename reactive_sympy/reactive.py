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

        vals = [sympy.simplify(v) for v in values]
        for s_val in self._values:
            if vals == s_val:
                return

        self._values.append(vals)

    def _is_resolved(self):
        return any([all([is_known_value(v) for v in vals]) for vals in self._values])

    def solutions(self):
        return [vals for vals in self._values if all([is_known_value(v) for v in vals])]


class ReactiveSympy:
    _all_symbols: list[ReactiveSymbol]
    _symbol_links: dict[ReactiveSymbol, list[ReactiveSymbol]]

    def __init__(self) -> None:
        self._all_symbols = []
        self._symbol_links = {}

    def symbols(self, names: str):
        symbs = sympy.symbols(names, cls=ReactiveSymbol)
        if isinstance(symbs, tuple):
            self._all_symbols.extend(symbs)
            return symbs
        else:
            self._all_symbols.append(symbs)
            return (symbs,)

    def link_symbol(self, symbol: ReactiveSymbol, vars: list[ReactiveSymbol]):
        self._symbol_links[symbol] = vars

    def eq(self, lhs: any, rhs: any) -> None:
        self._internal_eq(lhs, rhs)
        self.solve()

    def _internal_eq(self, lhs: any, rhs: any) -> None:
        expr = sympy.Eq(lhs, rhs)

        for sym in expr.free_symbols:
            solutions = sympy.solve(expr, sym)
            sym._add_values(solutions)

            link = self._symbol_links.get(sym, None)
            if link is not None:
                if len(link) != len(solutions):
                    print("no link here")

                if len(link) == len(solutions):
                    for li, s in zip(link, solutions):
                        li._add_values([s])

        print({s.name: s._values for s in expr.free_symbols}, end="\n\n")

    def solve(self):
        print("solving...")
        for symbol in self._all_symbols:
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
