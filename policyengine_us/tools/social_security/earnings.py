"""Shared annual indexing and highest-years selection for AIME calculations.

The legacy variable retains its existing year window and precision. The opt-in
history service supplies a complete career and requests statutory cent rounding.
"""

from decimal import Decimal
from fractions import Fraction

import numpy as np


def index_covered_earnings(amount, year_nawi, indexing_nawi, *, round_cents=False):
    if round_cents:
        # Convert first: annual records are exact money, not binary floats.
        result = (
            Fraction(str(amount))
            * Fraction(str(indexing_nawi))
            / Fraction(str(year_nawi))
        )
        cents = result * 100
        rounded = (2 * cents.numerator + cents.denominator) // (2 * cents.denominator)
        return Decimal(rounded) / 100
    return amount * (indexing_nawi / year_nawi)


def highest_earnings(earnings, years=35):
    """Select and zero-pad the highest years along the last array dimension.

    Object arrays preserve Decimal cents for the history service. Numeric arrays
    preserve the legacy variable's NumPy arithmetic and summation order.
    """
    values = np.asarray(earnings)
    selected = np.sort(values, axis=-1)[..., ::-1][..., :years]
    missing = years - selected.shape[-1]
    if missing > 0:
        shape = (*selected.shape[:-1], missing)
        # The legacy formula's padding is float64, including when annual
        # earnings arrived as float32. Preserve that promotion and sum exactly.
        dtype = object if selected.dtype == object else float
        selected = np.concatenate((selected, np.zeros(shape, dtype=dtype)), axis=-1)
    return selected
