import copy
import itertools

import sympy


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

    def _internal_eq(self, lhs: any, rhs: any) -> None:
        expr = sympy.Eq(lhs, rhs)
        for sym in expr.free_symbols:
            if len(sym.known_values) > 0:
                continue

            solutions = sympy.solve(expr, sym)
            solutions = [sympy.simplify(sol) for sol in solutions]
            sym._add_values(solutions)

    def eq(self, lhs: any, rhs: any) -> None:
        self._internal_eq(lhs, rhs)
        self._react()

    def _react(self):
        for s in self._all_symbols:
            if len(s.known_values) > 0:
                continue

            exprs = s._reactive_values
            new_exprs = []

            while len(exprs) > 0:
                ex = exprs.pop(0)
                if is_known_value(ex):
                    new_exprs.append(ex)
                    continue

                symb_values = []
                for symb in ex.free_symbols:
                    symb_values.append(
                        [sol for sol in symb.solutions if s not in sol.free_symbols]
                    )

                symb_value_combinations = list(itertools.product(*symb_values))
                if len(symb_value_combinations) == 0:
                    new_exprs.append(ex)
                    continue

                for combination in symb_value_combinations:
                    new_ex = copy.deepcopy(ex)
                    for sym, val in zip(ex.free_symbols, combination):
                        new_ex = sympy.simplify(new_ex.subs(sym, val))
                    new_exprs.append(new_ex)

            s._reactive_values = list(set(new_exprs))

        changed = False
        for s in self._all_symbols:
            if len(s.known_values) > 0:
                continue

            if len(s._reactive_values) <= 1:
                continue

            for lhs_i in range(len(s._reactive_values)):
                for rhs_j in range(lhs_i, len(s._reactive_values)):
                    changed = True
                    self._internal_eq(
                        s._reactive_values[lhs_i], s._reactive_values[rhs_j]
                    )

        if changed:
            self._react()


def is_known_value(v: any):
    if isinstance(v, (int, float, complex)):
        return True

    try:
        p = v.is_number
        return p
    except AttributeError:
        return False
