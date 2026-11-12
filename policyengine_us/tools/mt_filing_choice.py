"""Compare Montana joint and separate filing elections."""

TAX_TOLERANCE = 0.01


def mt_separate_filing_is_cheaper(separate_tax, joint_tax):
    """Keep joint filing unless separate filing saves more than one cent."""
    return separate_tax < joint_tax - TAX_TOLERANCE
