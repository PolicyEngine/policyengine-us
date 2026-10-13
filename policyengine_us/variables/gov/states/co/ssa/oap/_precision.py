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
# average is either exactly half a cent from a whole cent or at least $0.0008
# away. Float32 residue near $1,000 is about $0.00006, so $0.00005 of slack
# (half a hundredth of a cent) keeps a true half cent from rounding down.
_TIE_SLACK = 0.00005


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
    # Whole mills, with half a hundredth of a mill of slack for residue.
    mills = np.floor(amount * 1_000 + 0.05)
    return np.ceil(mills / 10) / 100
