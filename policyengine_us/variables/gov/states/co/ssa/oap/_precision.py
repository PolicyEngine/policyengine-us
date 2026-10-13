# Colorado records monthly income and grants in dollars and cents
# (9 CCR 2503-5 3.581(E) speaks of cents; 3.533 and 3.534 of $65, $20.00 and
# halves). Amounts the rule produces therefore fall on a half-cent grid:
# earnings are halved. Anything smaller is float32 residue (about $0.0001
# near $1,000) or the remainder of averaging an annual amount over twelve
# months, which a monthly record in cents does not hold. A quarter cent
# separates the two.
PRECISION = 0.0025
