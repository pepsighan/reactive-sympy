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

    def _internal_eq(self, lhs: any, rhs: any) -> None:
        expr = sympy.Eq(lhs, rhs)
        for sym in expr.free_symbols:
            if sym not in self._all_symbols:
                continue

            self.solve_expr_in_term_of(expr, sym)

    def solve_expr_in_term_of(
        self,
        expr: sympy.Expr,
        term: ReactiveSymbol,
    ):
        solutions = sympy.solve(expr, term)
        if isinstance(solutions, bool):
            return None

        term.add_values(solutions)
        self.sync_roots(term)

    def sync_roots(self, symbol: ReactiveSymbol):
        root_symbols = set([])
        if symbol in self._roots:
            root_symbols.add(symbol)
            roots = self._roots[symbol]
            for vals in symbol._values:
                if len(vals) == len(roots):
                    for root, val in zip(roots, vals):
                        root.add_values([val])

    def solve(self, answer: ReactiveSymbol, unknowns: set[ReactiveSymbol] = set()):
        unknowns = unknowns.union([answer])

        unknown_symbols = set([])
        for ans_vals in answer._values:
            for ans in ans_vals:
                symbols = [
                    sym
                    for sym in ans.free_symbols
                    if len(sym.solutions()) == 0 and sym not in unknowns
                ]
                unknown_symbols = unknown_symbols.union(symbols)

        unknowns = unknowns.union(unknown_symbols)
        for symbol in unknown_symbols:
            self.solve(symbol, unknowns)


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
