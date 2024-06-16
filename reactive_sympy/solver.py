import sympy


class SolverSymbol(sympy.Symbol):
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
        return [vals for vals in self.values if all([is_known_value(v) for v in vals])]


class SympySolver:
    _all_symbols: list[SolverSymbol]
    _symbol_appearance_order: list[SolverSymbol]

    _original_eqs: list[sympy.Eq]

    def __init__(self) -> None:
        self._all_symbols = []
        self._symbol_appearance_order = []
        self._original_eqs = []

    def answer_symbol(self):
        sym_name = "answer"

        existing_sym_names = [sym.name for sym in self._all_symbols]
        if sym_name in existing_sym_names:
            return self._all_symbols[existing_sym_names.index(sym_name)]

        return self.symbols(sym_name)

    def symbols(self, names: str, real: bool | None = None, **kwargs):
        symbs = sympy.symbols(
            names,
            cls=SolverSymbol,
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
            if sym not in self._symbol_appearance_order:
                self._symbol_appearance_order.extend(expr.free_symbols)

        self._original_eqs.append(expr)
        return expr

    def final_eq(self, lhs: any, rhs: any) -> sympy.Eq:
        if isinstance(rhs, sympy.Eq):
            if rhs.lhs in self._all_symbols:
                return self.eq(lhs, rhs.rhs)

            if rhs.rhs in self._all_symbols:
                return self.eq(lhs, rhs.lhs)

        return self.eq(lhs, rhs)

    def subs_eq(self, lhs: any, rhs: any = None) -> tuple[any, any]:
        if rhs is None:
            # Support subs with dictionary provided.
            if isinstance(lhs, dict):
                for key, value in lhs.items():
                    if key in self._all_symbols:
                        self.eq(key, value)
        else:
            self.eq(lhs, rhs)

        return self.answer_symbol(), self.answer_symbol()

    def solve(self, *args, **kwargs):
        # Solve expressions are eq expressions (if they are not already in which case the following case is False).
        if len(args) > 0:
            expr = sympy.Eq(args[0], 0)
            if expr != sympy.true and expr != sympy.false:
                self.eq(args[0], 0)

        return sympy.solve(*args, **kwargs)

    def solve_free_symbols(self, eq: any):
        resolved_all_symbols = True
        for sym in eq.free_symbols:
            if sym not in self._all_symbols:
                continue

            resolved = self.solve_expr_in_term_of(eq, sym)
            resolved_all_symbols = resolved and resolved_all_symbols

        return resolved_all_symbols

    def solve_expr_in_term_of(
        self,
        expr: sympy.Expr,
        term: SolverSymbol,
    ):
        solutions = sympy.solve(expr, term)
        if solutions == sympy.true or solutions == sympy.false:
            return False

        if len(solutions) == 0:
            return False

        term.add_values(solutions)
        return True

    def finalize(self):
        # for eq in self._original_eqs:
        #     self.solve_free_symbols(eq)

        ans_symbol = self.answer_symbol()

        for eq in self._original_eqs:
            for symbol in self._all_symbols:
                eq_syms = sympy.solve(eq, symbol)
                if len(eq_syms) == 0:
                    continue
                for an_eq in self._original_eqs:
                    if eq is an_eq:
                        continue

                    an_eq_syms = sympy.solve(an_eq, symbol)
                    if len(an_eq_syms) == 0:
                        continue

                    for lhs in an_eq_syms:
                        for eq_sym in eq_syms:
                            self.solve_free_symbols(sympy.Eq(lhs, eq_sym))

        sols = ans_symbol.solutions()
        sols = [sol for sol in sols if len(sol) == 1]
        if len(sols) == 0:
            return None

        return sols[0][0]


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
