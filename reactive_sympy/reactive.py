import sympy
import itertools
import copy


class ReactiveSymbol(sympy.Symbol):
    _reactive_values: list[any]

    def __new__(cls, name, **assumptions):
        val = super().__new__(cls, name, **assumptions)
        val._reactive_values = []
        return val

    @property
    def known_values(self):
        return [v for v in self._reactive_values if is_known_value(v)]

    @property
    def solutions(self):
        known = self.known_values
        if len(known) > 0:
            return known

        return self._reactive_values

    @property
    def _values(self):
        return self._reactive_values

    @_values.setter
    def value(self, v: any):
        v = [v]
        self._add_values(v)

    def _add_values(self, v: list[any]):
        if len(v) == 0:
            return

        self._reactive_values.extend(v)
        self._reactive_values = list(set(self._reactive_values))

    def __str__(self):
        return self.name


class ReactiveSympy:
    _all_symbols: list[ReactiveSymbol]

    def __init__(self) -> None:
        self._all_symbols = []

    def symbols(self, names: str):
        symbs = list(sympy.symbols(names, cls=ReactiveSymbol))
        self._all_symbols.extend(symbs)
        return symbs

    def eq(self, lhs: any, rhs: any) -> None:
        expr = sympy.Eq(lhs, rhs, evaluate=False)
        for sym in expr.free_symbols:
            solutions = sympy.solve(expr, sym)
            sym._add_values(solutions)
            self._react()

    def _react(self):
        for s in self._all_symbols:
            if len(s.known_values) > 0:
                continue

            exprs = [v for v in s._reactive_values]
            new_exprs = []

            while len(exprs) > 0:
                ex = exprs.pop(0)
                if is_known_value(ex):
                    continue

                unknowns = ex.free_symbols
                unknowns_values = []
                for unknown in unknowns:
                    sols = [
                        sol
                        for sol in unknown.solutions
                        if is_known_value(sol) or s not in sol.free_symbols
                    ]
                    unknowns_values.append(sols)

                unknown_combinations = list(itertools.product(*unknowns_values))
                for combination in unknown_combinations:
                    print(s, combination)
                    new_ex = copy.deepcopy(ex)
                    for sym, val in zip(unknowns, combination):
                        new_ex = sympy.simplify(new_ex.subs(sym, val))
                        # print(s, new_ex)
                    new_exprs.append(new_ex)

        s._reactive_values = new_exprs


def is_known_value(v: any):
    if isinstance(v, (int, float, complex)):
        return True

    try:
        p = v.is_number
        return p
    except AttributeError:
        return False
