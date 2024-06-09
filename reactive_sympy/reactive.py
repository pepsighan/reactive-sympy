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
        return any([all([is_known_value(v) for v in vals]) for vals in self._values])

    def solutions(self):
        return [vals for vals in self._values if all([is_known_value(v) for v in vals])]


class ExprHistory:
    _history_map = dict()

    def record_parent_expr(expr: any, history_expr: list[any]):
        expr = str(expr)
        history_expr = [str(h) for h in history_expr]
        if ExprHistory._history_map.get(expr) is None:
            ExprHistory._history_map[expr] = []

        vals = ExprHistory._history_map.get(expr)
        vals.extend(history_expr)

    def linked_expr(expr: str, acc: set[str]):
        vals = ExprHistory._history_map.get(expr)
        if vals is None:
            return

        new_acc = set([])
        for val in vals:
            if val not in acc:
                acc.add(val)
                new_acc.add(val)

        for v in new_acc:
            ExprHistory.linked_expr(v, acc)

    def is_expr_in_history(expr: any, other: any):
        expr = str(expr)
        other = str(other)
        vals = set([])
        ExprHistory.linked_expr(expr, vals)

        for val in vals:
            if other == val:
                return True

        return False


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
        lhs = sympy.simplify(lhs)
        rhs = sympy.simplify(rhs)
        if ExprHistory.is_expr_in_history(lhs, rhs) or ExprHistory.is_expr_in_history(
            rhs, lhs
        ):
            print("ignored")
            # Either of the expression already uses the other statement. So, no new meaning is to be found.
            return

        expr = sympy.Eq(lhs, rhs)

        for sym in expr.free_symbols:
            solutions = sympy.solve(expr, sym)
            solutions = [sympy.simplify(s) for s in solutions]
            for sol in solutions:
                ExprHistory.record_parent_expr(sol, [lhs, rhs])

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
