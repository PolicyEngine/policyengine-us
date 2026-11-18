import numpy as np

# Colorado records monthly income and grants in dollars and cents
# (9 CCR 2503-5 3.581(E) speaks of cents; 3.533 and 3.534 of $65, $20.00 and
# halves). The OAP variables therefore take each monthly amount in cents:
# income averaged from an annual amount (3.520.781(G)) to the nearest cent,
# half a cent rounded up, and SSI as SSA pays it. The rule's own arithmetic
# then stays on a half-cent grid (earnings are halved), and anything smaller
# than a tenth of a cent is float32 residue.
PRECISION = 0.001

# Annual amounts in cents average to multiples of 1/1,200 of a dollar, so an
# average is either exactly a half cent past a whole cent or at least $0.00083
# away from one. Storing the annual amount in float32 and then dividing it by
# 12 in float32 leaves about $0.0001 of residue near $1,000 a month, so $0.0004
# of slack, about halfway between, keeps a true half cent from rounding down
# without moving any other average across a tie. That holds for a monthly
# amount from one source below about $4,000; above that, float32 cannot
# resolve the 1/1,200 grid, and a tie can round either way.
_TIE_SLACK = 0.0004


def cents(amount):
    """A monthly amount to the nearest cent, half a cent rounded up."""
    amount = np.asarray(amount, dtype=np.float64)
    return np.floor(amount * 100 + 0.5 + _TIE_SLACK * 100) / 100


def ssi_paid(amount):
    """A monthly SSI amount as SSA pays it.

    POMS SI 02001.010: a fractional cent of at least a tenth of a cent raises
    the payment to the next higher cent; a smaller one is dropped.
    """
    amount = np.asarray(amount, dtype=np.float64)
    # Whole mills, with half a tenth of a mill ($0.00005) of slack for
    # float32 residue.
    mills = np.floor(amount * 1_000 + 0.05)
    return np.ceil(mills / 10) / 100
