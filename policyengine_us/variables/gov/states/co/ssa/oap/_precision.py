import numpy as np

# Colorado records monthly income and grants in dollars and cents
# (9 CCR 2503-5 3.581(E) speaks of cents; 3.533 and 3.534 of $65, $20.00 and
# halves). The OAP variables therefore take each monthly amount in cents:
# income averaged from an annual amount (3.520.781(G)) to the nearest cent,
# and SSI as SSA pays it. The rule's own arithmetic then stays on a half-cent
# grid (earnings are halved), and anything smaller than a tenth of a cent is
# float32 residue.
PRECISION = 0.001


def cents(amount):
    """A monthly amount to the nearest cent."""
    return np.round(np.asarray(amount, dtype=np.float64), 2)


def ssi_paid(amount):
    """A monthly SSI amount as SSA pays it.

    POMS SI 02001.010: a fractional cent of at least a tenth of a cent raises
    the payment to the next higher cent; a smaller one is dropped.
    """
    mills = np.floor(np.asarray(amount, dtype=np.float64) * 1_000 + PRECISION)
    return np.ceil(mills / 10) / 100
