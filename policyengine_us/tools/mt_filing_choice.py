"""Compare Montana joint and separate filing elections."""

import numpy as np

TAX_TOLERANCE = 0.01


def mt_separate_filing_is_cheaper(separate_tax, joint_tax, separate_tax_magnitude=None):
    """Require savings above one cent plus float32 roundoff."""
    separate = np.asarray(separate_tax, dtype=np.float64)
    joint = np.asarray(joint_tax, dtype=np.float64)
    magnitude = (
        np.abs(separate)
        if separate_tax_magnitude is None
        else np.asarray(separate_tax_magnitude, dtype=np.float64)
    )
    # Core stores each column and the joint tax in float32, then sums the
    # separate columns in float64. Allow their float32 input rounding before
    # comparing the savings in float64. After refundable credits, pass the
    # sum of absolute columns so offsetting taxes do not hide rounding.
    roundoff = np.finfo(np.float32).eps * np.maximum(magnitude, np.abs(joint))
    return joint - separate > TAX_TOLERANCE + roundoff
