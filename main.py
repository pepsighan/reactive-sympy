from reactive_sympy.solver import SympySolver
import sympy as sp

sy = SympySolver()
answer = sy.answer_symbol()


def sympy_expression(sy):
    # Let the variables be defined as follows:
    x, y = sy.symbols("x y")

    # Given equation
    equation_1 = sp.Abs(x - 2 * y) + sp.Abs(y - 2 * x) - 40

    # Expression which we want to minimize
    expr = 5 * x**2 + 5 * y**2 - 8 * x * y

    # Apply constraint equation_1 to the expression expr
    expression = expr.subs(*sy.subs_eq(sy.solve(equation_1, y)[0]))

    return expression


result = sympy_expression(sy)
sy.final_eq(answer, result)
final_answer = sy.finalize()

print(final_answer)
