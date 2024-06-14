import sympy


class ReactiveSymbol(sympy.Symbol):
    values: list[any]

    def __new__(cls, name, **assumptions):
        val = super().__new__(cls, name, **assumptions)
        val.values = []
        return val

    def keep_unique(self):
        vals = []
        for existing_vals in self.values:
            found = any([new_vals == existing_vals for new_vals in vals])
            if found:
                continue
            vals.append(existing_vals)
        self.values = vals

    def add_values(self, v: list[any]):
        if len(v) == 0:
            return
        self.values.append(v)
        self.keep_unique()

    def solutions(self):
        return [
            vals
            for vals in self.values
            if all([is_known_value(v) for v in vals]) and len(vals) == 1
        ]


class ReactiveSympy:
    _all_symbols: list[ReactiveSymbol]

    _original_eqs: list[sympy.Eq] = []

    def __init__(self) -> None:
        self._all_symbols = []

    def answer_symbol(self):
        return self.symbols("answer")

    def symbols(self, names: str, real: bool | None = None, **kwargs):
        symbs = sympy.symbols(
            names,
            cls=ReactiveSymbol,
            real=True if real is None else real,
            **kwargs,
        )
        if isinstance(symbs, tuple):
            self._all_symbols.extend(symbs)
            return symbs
        else:
            self._all_symbols.append(symbs)
            return symbs

    def eq(self, lhs: any, rhs: any) -> sympy.Eq:
        expr = sympy.Eq(lhs, rhs)
        for sym in expr.free_symbols:
            if sym not in self._all_symbols:
                continue

            self.solve_expr_in_term_of(expr, sym)
        return expr

    def solve(self, *args, **kwargs):
        if len(args) > 0:
            self.eq(args[0], 0)

        return sympy.solve(*args, **kwargs)

        for sym, val in contiguous_results.items():
            sym.add_values(val)

        return sympy.solve(*args, **kwargs)

    def solve_expr_in_term_of(
        self,
        expr: sympy.Expr,
        term: ReactiveSymbol,
    ):
        solutions = sympy.solve(expr, term)
        if isinstance(solutions, bool):
            return None

        term.add_values(solutions)

    def replace_found_value_in_expr(self):
        found_values = {
            symbol: symbol.solutions()[0]
            for symbol in self._all_symbols
            if len(symbol.solutions()) > 0
        }

        for symbol in self._all_symbols:
            for values in symbol.values:
                for i in range(len(values)):
                    for v_sym, v_value in found_values.items():
                        ans = sympy.simplify(values[i].subs(v_sym, v_value[0]))
                        if ans == sympy.nan:
                            continue

                        values[i] = ans
            symbol.keep_unique()

    def finalize(self):
        self.replace_found_value_in_expr()

        for symbol in self._all_symbols:
            single_vals = [vals for vals in symbol.values if len(vals) == 1]
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
