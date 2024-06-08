import sys
import sympy
import itertools
import copy


class ReactiveSymbol(sympy.Symbol):
    _values: list[any]

    def __new__(cls, name, **assumptions):
        val = super().__new__(cls, name, **assumptions)
        val._values = []
        return val

    @property
    def known_values(self):
        return [v for v in self._values if is_known_value(v)]

    @property
    def solutions(self):
        known = self.known_values
        if len(known) > 0:
            return known

        return self._values

    @property
    def _internal_values(self):
        return self._values

    @_internal_values.setter
    def value(self, v: any):
        v = [v]
        self._add_values(v)

    def _sort_values(self):
        self._values = sorted(
            list(set(self._values)),
            key=lambda x: 0 if is_known_value(x) else len(x.free_symbols),
        )

    def _add_values(self, v: list[any]):
        if len(v) == 0:
            return

        self._values.extend([sympy.simplify(it) for it in v])
        self._sort_values()

    def distance_to_solution(self, symbols: set["ReactiveSymbol"] = set([])) -> int:
        if len(self.known_values):
            return 0

        more_symbols = set([*symbols, self])

        dists = []
        for v in self._values:
            for sym in v.free_symbols:
                if sym in more_symbols:
                    continue

                dists.append(sym.distance_to_solution(more_symbols))

        return min(dists) + 1

    def __str__(self):
        return self.name


class ReactiveSympy:
    _all_symbols: list[ReactiveSymbol]

    def __init__(self) -> None:
        self._all_symbols = []

    def symbols(self, names: str):
        symbs = sympy.symbols(names, cls=ReactiveSymbol)
        if isinstance(symbs, tuple):
            self._all_symbols.extend(symbs)
            return symbs
        else:
            self._all_symbols.append(symbs)
            return (symbs,)

    def eq(self, lhs: any, rhs: any) -> None:
        expr = sympy.Eq(lhs, rhs)
        for sym in expr.free_symbols:
            solutions = sympy.solve(expr, sym)
            sym._add_values(solutions)

        print({s.name: s.solutions for s in self._all_symbols}, end="\n\n")

    def solve(self):
        while True:
            sorted_symbols = sorted(
                self._all_symbols,
                key=lambda x: sys.maxsize  # No need to solve this again.
                if len(x.solutions) > 0
                else min(len(x.free_symbols) for x in x._values),
            )
            focused_symb = sorted_symbols.pop(0)

            if len(focused_symb.known_values) > 0:
                continue

            for expr in focused_symb._values:
                values = [
                    [
                        value
                        for value in free_symb._values
                        if is_known_value(value)
                        or focused_symb not in value.free_symbols
                    ]
                    for free_symb in expr.free_symbols
                ]

                value_symbs = [
                    free_symb
                    for free_symb, val in zip(expr.free_symbols, values)
                    if len(val) > 0
                ]
                values = [v for v in values if len(v) > 0]
                values_combo = list(itertools.product(*values))

                for values in values_combo:
                    sub_expr = copy.deepcopy(expr)
                    for i, (symb, value) in enumerate(zip(value_symbs, values)):
                        if value_contains_previous_symbols(value, value_symbs[:i]):
                            continue

                        sub_expr = sympy.simplify(sub_expr.subs(symb, value))

                    if expr is not sub_expr:
                        ex_distance = min(
                            [sym.distance_to_solution() for sym in expr.free_symbols]
                        )
                        sub_ex_distance = min(
                            [
                                sym.distance_to_solution()
                                for sym in sub_expr.free_symbols
                            ]
                        )
                        # print(
                        #     focused_symb,
                        #     "=>",
                        #     ex_distance,
                        #     "=",
                        #     ex,
                        #     ",",
                        #     sub_ex_distance,
                        #     "=",
                        #     sub_ex,
                        # )
                        if sub_ex_distance < ex_distance:
                            # print("+++" * 20)
                            # print(ex)
                            # print("---" * 20)
                            # print(sub_ex)
                            # print("+++" * 20)
                            self.eq(focused_symb, sub_expr)

            done = all([len(s.known_values) > 0 for s in self._all_symbols])
            if done:
                break


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
