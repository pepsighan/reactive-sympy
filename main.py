from reactive_sympy.solver import SympySolver
import sympy as sp

sy = SympySolver()
answer = sy.answer_symbol()


def sympy_expression(sy):
    # Let the variables be defined as follows:
    # x: The maximum possible number of yellow numbers

    x = sy.symbols("x")

    # The sum of any two yellow numbers should be a blue number.
    # So, the total sum of all yellow numbers should be equal to the total sum of all blue numbers.
    yellow_total_sum = x * (x - 1) / 2

    # The total number of three-digit numbers is (999 - 111 + 1) = 899.
    # The sum of all three-digit numbers from 111 to 999 is (sum of 111 and 999) * number of terms / 2 = (111 + 999) * 899 / 2 = 450000.
    blue_total_sum = 450000

    # Equating the two sums gives us an equation: x*(x-1)/2 = 450000
    equation = sy.eq(yellow_total_sum, blue_total_sum)

    return equation


result = sympy_expression(sy)
sy.final_eq(answer, result)
final_answer = sy.finalize()

print(final_answer)

for sym in sy._all_symbols:
    print(f"{sym} = {sym.values}")
