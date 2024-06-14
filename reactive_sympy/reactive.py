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
        print(self.name, self.values, vals)

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
        sym_name = "answer"

        existing_sym_names = [sym.name for sym in self._all_symbols]
        if sym_name in existing_sym_names:
            return self._all_symbols[existing_sym_names.index(sym_name)]

        return self.symbols(sym_name)

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
        self._original_eqs.append(expr)
        return expr

    def solve(self, *args, **kwargs):
        # Solve expressions are eq expressions (if they are not already in which case the following case is False).
        if len(args) > 0 and sympy.Eq(args[0], 0):
            self.eq(args[0], 0)

        return sympy.solve(*args, **kwargs)

    def solve_free_symbols(self, eq: any):
        ans = self.answer_symbol()
        has_ans_sym = ans in eq.free_symbols
        for sym in eq.free_symbols:
            if has_ans_sym and sym != ans:
                # For a equation with answer symbol, do not solve for other symbols.
                continue

            if sym not in self._all_symbols:
                continue

            self.solve_expr_in_term_of(eq, sym)
        return eq

    def solve_expr_in_term_of(
        self,
        expr: sympy.Expr,
        term: ReactiveSymbol,
    ):
        solutions = sympy.solve(expr, term)
        if solutions == sympy.true or solutions == sympy.false:
            return None

        term.add_values(solutions)

    def finalize(self):
        for eq in self._original_eqs:
            self.solve_free_symbols(eq)

        for symbol in self._all_symbols:
            single_vals = [vals for vals in symbol.values if len(vals) == 1]
            for i in range(len(single_vals)):
                lhs = single_vals[i][0]
                for eq in self._original_eqs:
                    if symbol not in eq.free_symbols:
                        continue

                    eq_syms = sympy.solve(eq, symbol)
                    if len(eq_syms) == 0:
                        continue

                    for eq_sym in eq_syms:
                        solve_eq = sympy.Eq(lhs, eq_sym)
                        if solve_eq == sympy.true or solve_eq == sympy.false:
                            continue

                        self.solve_free_symbols(solve_eq)


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
