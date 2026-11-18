import numpy as np

# Section 3.111(H) lists the guideline in cents and the model rounds monthly
# income to cents, so an exact fee has at most five decimal places. Float64
# arithmetic on those amounts strays from the exact fee by about $0.000000000001.
# This tolerance brings a fee that should come to whole dollars up to them, and
# it can't reach the next possible fee, $0.00001 away.
WHOLE_DOLLAR_TOLERANCE = 1e-9


def drop_cents(amount):
    return np.floor(amount + WHOLE_DOLLAR_TOLERANCE)


def income_and_guideline_in_cents(spm_unit, period):
    """Return monthly countable income, never below zero, and the guideline.

    Variables store float32, which can't hold most amounts in cents, so this
    rounds each amount to cents in float64.
    """
    income = np.asarray(spm_unit("co_ccap_countable_income", period), dtype=np.float64)
    guideline = np.asarray(spm_unit("co_ccap_fpg", period), dtype=np.float64)
    return np.round(np.maximum(income, 0), 2), np.round(guideline, 2)
