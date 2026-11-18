"""Pure historical COLA rounding, separate from reported-source factors.

The initial-PIA benchmark-year rule is a different operation. This module
implements the rounding of an existing PIA after each historical COLA.
"""

from decimal import Decimal, ROUND_CEILING, ROUND_DOWN


COLA_ROUND_UP_TO_DIME = 1
COLA_ROUND_DOWN_TO_DIME = 2


def validate_cola_rounding_rule(rounding_rule):
    """Reject historical rules that have no implemented rounding operation.

    Codes come from ``gov.ssa.cola_history.pia_rounding``. Validate every
    exposed event before using a cohort's history, including baseline events
    which cancel from a proportional reform factor.
    """
    if isinstance(rounding_rule, bool) or rounding_rule not in (
        COLA_ROUND_UP_TO_DIME,
        COLA_ROUND_DOWN_TO_DIME,
    ):
        raise ValueError(
            f"Unsupported historical COLA rounding rule: {rounding_rule!r}"
        )
    return rounding_rule


def apply_cola_to_pia(pia, rate, rounding_rule):
    """Apply one COLA to a monthly PIA and return an exactly rounded Decimal.

    POMS RS 00601.020 A specifies upward dime rounding before June 1982 and
    downward dime rounding from June 1982. POMS RS 00605.021 C gives a worked
    1979-1982 sequence using both rules. Conversion through decimal strings
    avoids importing binary floating-point error into a statutory dime boundary.
    """
    rule = validate_cola_rounding_rule(rounding_rule)
    pia = Decimal(str(pia))
    rate = Decimal(str(rate))
    if not pia.is_finite() or not rate.is_finite() or pia < 0 or rate < 0:
        raise ValueError("PIA and statutory COLA rate must be finite and nonnegative")
    rounding = ROUND_CEILING if rule == COLA_ROUND_UP_TO_DIME else ROUND_DOWN
    return (pia * (1 + rate)).quantize(Decimal("0.1"), rounding=rounding)
