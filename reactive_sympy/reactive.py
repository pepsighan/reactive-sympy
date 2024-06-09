import sympy


class ReactiveSymbol(sympy.Symbol):
    _values: list[any]

    def __new__(cls, name, **assumptions):
        val = super().__new__(cls, name, **assumptions)
        val._values = []
        return val

    def keep_unique(self):
        vals = []
        for existing_vals in self._values:
            found = any([new_vals == existing_vals for new_vals in vals])
            if found:
                continue
            vals.append(existing_vals)
        self._values = vals

    def add_values(self, v: list[any]):
        if len(v) == 0:
            return
        self._values.append(v)
        self.keep_unique()

    def solutions(self):
        return [vals for vals in self._values if all([is_known_value(v) for v in vals])]


class ReactiveSympy:
    _all_symbols: list[ReactiveSymbol]
    _roots: dict[ReactiveSymbol, set[ReactiveSymbol]]

    def __init__(self) -> None:
        self._all_symbols = []
        self._roots = {}

    def symbols(self, names: str):
        symbs = sympy.symbols(names, cls=ReactiveSymbol)
        if isinstance(symbs, tuple):
            self._all_symbols.extend(symbs)
            return symbs
        else:
            self._all_symbols.append(symbs)
            return (symbs,)

    def set_roots(self, symbol: ReactiveSymbol, roots: list[ReactiveSymbol]):
        assert symbol not in self._roots
        self._roots[symbol] = roots

    def eq(self, lhs: any, rhs: any) -> None:
        self._internal_eq(lhs, rhs)
        # self.solve()

    def _internal_eq(self, lhs: any, rhs: any) -> None:
        expr = sympy.Eq(lhs, rhs)
        for sym in expr.free_symbols:
            if sym not in self._all_symbols:
                continue

            solutions = sympy.solve(expr, sym)
            sym.add_values(solutions)

    def expr_in_terms(self, lhs: any, rhs: any, term: any) -> any:
        expr = sympy.Eq(lhs, rhs)
        val = sympy.solve(expr, term)
        if isinstance(val, bool):
            return None
        return [sympy.simplify(s) for s in val]

    def sync_roots(self):
        root_symbols = set([])
        for symbol in self._all_symbols:
            if symbol in self._roots:
                root_symbols.add(symbol)
                roots = self._roots[symbol]
                for vals in symbol._values:
                    if len(vals) == len(roots):
                        for root, val in zip(roots, vals):
                            root.add_values([val])

        for sym in root_symbols:
            self._all_symbols.remove(sym)

        for sym in self._all_symbols:
            remove_vals = []
            for sym_values in sym._values:
                for removed_sym in root_symbols:
                    for sym_val in sym_values:
                        if is_known_value(sym_val):
                            continue

                        if removed_sym in sym_val.free_symbols:
                            remove_vals.append(sym_values)

            for val in remove_vals:
                sym._values.remove(val)

    def solve(self, answer: ReactiveSymbol):
        self.sync_roots()

        while len(answer.solutions()) == 0:
            combinations = []
            for symbol in self._all_symbols:
                for i in range(len(symbol._values)):
                    lhses = symbol._values[i]
                    for j in range(i + 1, len(symbol._values)):
                        rhses = symbol._values[j]
                        for lhs in lhses:
                            for rhs in rhses:
                                combinations.append((lhs, rhs))

            complexity = sorted(
                [sympy.Eq(c[0], c[1]).count_ops() for c in combinations]
            )
            max_complexity = complexity[:4]
            combinations = [
                c
                for c in combinations
                if sympy.Eq(c[0], c[1]).count_ops() <= max_complexity[-1]
            ]
            for lhs, rhs in combinations:
                self._internal_eq(lhs, rhs)


def symbols_of(expr: any):
    return expr.free_symbols


def is_known_value(v: any):
    if isinstance(v, (int, float, complex)):
        return True

    try:
        p = v.is_number
        return p
    except AttributeError:
        return False
