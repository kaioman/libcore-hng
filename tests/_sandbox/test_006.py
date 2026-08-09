from libcore_hng.utils.mathops import *

value = 12.34567
print(roundx(value, Fraction.FLOOR, 2))

value = 12.34567
print(roundx(value, Fraction.FLOOR, 0))

value = 12.34567
print(roundx(value, Fraction.HALF_UP, 0))

value = 12.34567
print(roundx(value, Fraction.CEILING, 0))

value = 12135
value_r = roundx(value, Fraction.FLOOR, -2)
print(value_r)

value = 12135
value_r = roundx(value, Fraction.FLOOR, -3)
print(value_r)

value = 12.45
value_r = roundx(value, Fraction.HALF_UP, 1)
print(value_r)

value = 12.44
value_r = roundx(value, Fraction.HALF_UP, 1)
print(value_r)

value = 12.44
value_r = roundx(value, Fraction.CEILING, 1)
print(value_r)

value = 12.44
value_r = roundx(value, Fraction.FLOOR, 0)
print(value_r)
