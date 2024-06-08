import sympy


class ReactiveSymbol(sympy.Symbol):
    _reactive_value: any = None

    @property
    def value(self):
        return self._reactive_value

    @value.setter
    def value(self, v: any):
        self._reactive_value = v

    def __str__(self):
        if self._reactive_value is None:
            return self.name

        return f"{self.name} = {self.value}"


def reactive_symbol(names: str) -> list[ReactiveSymbol]:
    return list(sympy.symbols(names, cls=ReactiveSymbol))
