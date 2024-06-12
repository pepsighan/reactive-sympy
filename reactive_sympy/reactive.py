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
        return [
            vals
            for vals in self._values
            if all([is_known_value(v) for v in vals]) and len(vals) == 1
        ]


class ReactiveSympy:
    _all_symbols: list[ReactiveSymbol]
    _roots: dict[ReactiveSymbol, set[ReactiveSymbol]]

    def __init__(self) -> None:
        self._all_symbols = []
        self._roots = {}

    def symbols(self, names: str):
        symbs = sympy.symbols(names, cls=ReactiveSymbol, real=True)
        if isinstance(symbs, tuple):
            self._all_symbols.extend(symbs)
            return symbs
        else:
            self._all_symbols.append(symbs)
            return symbs

    def set_roots(self, symbol: ReactiveSymbol, roots: list[ReactiveSymbol]):
        assert symbol not in self._roots
        self._roots[symbol] = roots

    def eq(self, lhs: any, rhs: any) -> sympy.Eq:
        expr = sympy.Eq(lhs, rhs)
        for sym in expr.free_symbols:
            if sym not in self._all_symbols:
                continue

            self.solve_expr_in_term_of(expr, sym)
        return expr

    def solve(self, *args, **kwargs):
        dict_is = kwargs.pop("dict", True)
        results = sympy.solve(*args, **kwargs, dict=True)
        contiguous_results = {}
        for result in results:
            for sym, val in result.items():
                if sym not in contiguous_results:
                    contiguous_results[sym] = []
                contiguous_results[sym].append(val)

        for sym, val in contiguous_results.items():
            sym.add_values(val)

        return sympy.solve(*args, **kwargs, dict=dict_is)

    def solve_expr_in_term_of(
        self,
        expr: sympy.Expr,
        term: ReactiveSymbol,
    ):
        solutions = sympy.solve(expr, term)
        if isinstance(solutions, bool):
            return None

        term.add_values(solutions)
        self.sync_roots()

    def sync_roots(self):
        for symbol in self._all_symbols:
            if symbol in self._roots:
                roots = self._roots[symbol]
                for vals in symbol._values:
                    if len(vals) == len(roots):
                        for root, val in zip(roots, vals):
                            root.add_values([val])

                        for oth_sym in self._all_symbols:
                            if oth_sym is symbol:
                                continue

                            for root in roots:
                                for oth_vals in oth_sym._values:
                                    oth_val_replacements = []
                                    for oth_val in oth_vals:
                                        if symbol in symbols_of(oth_val):
                                            oth_val_replacements.append(
                                                oth_val.subs(symbol, root)
                                            )

                                    if len(oth_val_replacements) > 0:
                                        oth_sym.add_values(oth_val_replacements)

    def replace_found_value_in_expr(self):
        found_values = {
            symbol: symbol.solutions()[0]
            for symbol in self._all_symbols
            if len(symbol.solutions()) > 0
        }

        for symbol in self._all_symbols:
            for values in symbol._values:
                for i in range(len(values)):
                    for v_sym, v_value in found_values.items():
                        ans = sympy.simplify(values[i].subs(v_sym, v_value[0]))
                        if ans == sympy.nan:
                            continue

                        values[i] = ans

    def finalize(self):
        self.replace_found_value_in_expr()

        for symbol in self._all_symbols:
            single_vals = [vals for vals in symbol._values if len(vals) == 1]
            for i in range(len(single_vals)):
                for j in range(i + 1, len(single_vals)):
                    lhs = single_vals[i][0]
                    rhs = single_vals[j][0]
                    self.eq(lhs, rhs)

        self.replace_found_value_in_expr()


def symbols_of(expr: any):
    if is_known_value(expr):
        return {}

    return expr.free_symbols


def is_known_value(v: any):
    if isinstance(v, (int, float, complex)):
        return True

    try:
        p = v.is_number
        return p
    except AttributeError:
        return False
