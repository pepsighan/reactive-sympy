import sympy


class ReactiveSymbol(sympy.Symbol):
    _reactive_value: any = None

    def set_value(self, v: any):
        self._reactive_value = v

    def __str__(self):
        if self._reactive_value is None:
            return super.__str__(self)

        return f"{super.__str__(self)} = {self._reactive_value}"


def reactive_symbol(names: str):
    return sympy.symbols(names, cls=ReactiveSymbol)
