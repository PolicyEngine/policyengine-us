"""Statutory COLA events for the opt-in household calculator.

Amounts are monthly dollars.  The December COLA changes the following January
check; ``payment_month`` always denotes the check month, not entitlement month.
Historical observations and rounding rules come from SSA, never SOI uprating.
"""

from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from typing import Iterable, Mapping


DIME = Decimal("0.1")


def _decimal(value) -> Decimal:
    result = Decimal(str(value))
    if not result.is_finite():
        raise ValueError("A COLA amount or rate must be finite")
    return result


def _month(value) -> str:
    if isinstance(value, date):
        return value.strftime("%Y-%m")
    result = str(value)
    try:
        parsed = date.fromisoformat(result + "-01" if len(result) == 7 else result)
    except ValueError as error:
        raise ValueError("A COLA month must be YYYY-MM or an ISO date") from error
    return parsed.strftime("%Y-%m")


def floor_dime(value) -> Decimal:
    value = value if isinstance(value, Fraction) else Fraction(_decimal(value))
    dimes = value * 10
    return Decimal(dimes.numerator // dimes.denominator) / 10


def _ceil_dime(value) -> Decimal:
    value = value if isinstance(value, Fraction) else Fraction(_decimal(value))
    dimes = value * 10
    return Decimal(-(-dimes.numerator // dimes.denominator)) / 10


@dataclass(frozen=True)
class ColaEvent:
    effective_month: str
    payment_month: str
    rate: Decimal
    rounding: str = "dime_floor"
    # December 1999 was paid at 2.4% until the July 2001 adjustment, when SSA
    # recomputed the 1999/2000 increases at 2.5%/3.5%.  Keeping both values
    # reproduces ordinary checks before and after the correction.  The special
    # one-time arrears payment is outside this gross recurring-benefit service.
    as_paid_rate: Decimal | None = None
    correction_payment_month: str | None = None

    def __post_init__(self):
        object.__setattr__(self, "effective_month", _month(self.effective_month))
        object.__setattr__(self, "payment_month", _month(self.payment_month))
        object.__setattr__(self, "rate", _decimal(self.rate))
        if self.rate < 0 or self.payment_month <= self.effective_month:
            raise ValueError("COLAs require a nonnegative rate and later check month")
        if self.as_paid_rate is not None:
            object.__setattr__(self, "as_paid_rate", _decimal(self.as_paid_rate))
            if self.as_paid_rate < 0 or self.correction_payment_month is None:
                raise ValueError("An as-paid COLA requires its correction month")
        if self.correction_payment_month is not None:
            object.__setattr__(
                self, "correction_payment_month", _month(self.correction_payment_month)
            )

    def rate_at_valuation(self, payment_month) -> Decimal:
        if (
            self.as_paid_rate is not None
            and _month(payment_month) < self.correction_payment_month
        ):
            return self.as_paid_rate
        return self.rate


def exposed_events(eligibility_year, payment_month, events) -> tuple[ColaEvent, ...]:
    """Select events from the benchmark year, including pre-claim COLAs."""
    if int(eligibility_year) < 1983:
        raise ValueError("COLA calculations require a benchmark year of 1983 or later")
    target = _month(payment_month)
    selected = tuple(
        sorted(
            (
                event
                for event in events
                if int(event.effective_month[:4]) >= int(eligibility_year)
                and event.payment_month <= target
            ),
            key=lambda event: event.payment_month,
        )
    )
    if len({event.payment_month for event in selected}) != len(selected):
        raise ValueError("Duplicate COLA payment months are ambiguous")
    for event in selected:
        if event.rounding != "dime_floor" or event.effective_month < "1982-06":
            raise ValueError("The applicable historical COLA rounding is unsupported")
    return selected


def apply_colas(pia, eligibility_year, payment_month, events) -> Decimal:
    """Truncate the eligibility PIA and truncate again after every COLA."""
    result = _decimal(pia)
    if result < 0:
        raise ValueError("PIA must be nonnegative")
    result = floor_dime(result)
    for event in exposed_events(eligibility_year, payment_month, events):
        result = floor_dime(
            Fraction(result) * (1 + Fraction(event.rate_at_valuation(payment_month)))
        )
    return result


def cola_factor(eligibility_year, payment_month, events) -> Decimal:
    """Unrounded accumulation for diagnostics; not a replacement for apply_colas."""
    result = Decimal(1)
    for event in exposed_events(eligibility_year, payment_month, events):
        result *= 1 + event.rate_at_valuation(payment_month)
    return result


def reverse_colas_interval(lower, upper, eligibility_year, payment_month, events):
    """Exact half-open preimage on the eligibility-PIA dime lattice.

    Fraction endpoints are accepted to preserve an exact amount/ratio division.
    Each returned endpoint is a dime.  An eligibility PIA on that lattice is
    admissible iff lower <= PIA < upper; an empty preimage raises ValueError.
    This carries payment-rounding uncertainty backward instead of dividing a
    rounded check by an unrounded cumulative COLA factor.
    """
    lower, upper = _ceil_dime(lower), _ceil_dime(upper)
    if lower < 0 or lower >= upper:
        raise ValueError("A PIA interval must be nonnegative and nonempty")
    for event in reversed(exposed_events(eligibility_year, payment_month, events)):
        factor = 1 + Fraction(event.rate_at_valuation(payment_month))
        lower, upper = (
            _ceil_dime(Fraction(lower) / factor),
            _ceil_dime(Fraction(upper) / factor),
        )
        if lower >= upper:
            raise ValueError("The supplied payment interval has no eligible PIA")
    return lower, upper


def adjusted_events(
    events: Iterable[ColaEvent],
    rate_changes: Mapping[int, Decimal] | None = None,
    withheld_years: Iterable[int] = (),
) -> tuple[ColaEvent, ...]:
    """Apply percentage-point changes and withholding jointly, exactly once.

    Keys denote check calendar years.  A withheld event has rate zero even if a
    rate increase is also selected.  Preserve the supplied precision after a
    policy addition, and floor the proposed COLA at zero.
    """
    changes = rate_changes or {}
    withheld = set(withheld_years)
    result = []
    for event in events:
        year = int(event.payment_month[:4])
        delta = _decimal(changes.get(year, 0))
        rate = Decimal(0) if year in withheld else max(Decimal(0), event.rate + delta)
        paid = event.as_paid_rate
        if paid is not None:
            paid = Decimal(0) if year in withheld else max(Decimal(0), paid + delta)
        result.append(replace(event, rate=rate, as_paid_rate=paid))
    return tuple(result)


def projected_events(
    q3_by_payment_year: Mapping[int, Decimal],
) -> tuple[ColaEvent, ...]:
    """Freeze statutory rounded rates from January-keyed Q3 index levels.

    The first observation is the last effective-COLA anchor.  Zero-COLA years
    retain that anchor; a new positive rate advances it.  SSA rounds a positive
    fractional rate to .001 (one tenth of one percentage point), half up.
    """
    observations = sorted(
        (int(year), _decimal(value)) for year, value in q3_by_payment_year.items()
    )
    if not observations or any(value <= 0 for _, value in observations):
        raise ValueError("Projection requires a positive Q3-index anchor and path")
    anchor_year, high_water = observations[0]
    result = []
    for year, level in observations[1:]:
        if year != anchor_year + 1:
            raise ValueError("The projected Q3 path must contain consecutive years")
        rate = max(
            Decimal(0),
            (level / high_water - 1).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP),
        )
        result.append(ColaEvent(f"{year - 1}-12", f"{year}-01", rate))
        if rate > 0:
            high_water = level
        anchor_year = year
    return tuple(result)


def read_parameter_events(parameters, through_year: int) -> tuple[ColaEvent, ...]:
    """Read authored statutory history and freeze projected runtime SSA Q3 data.

    ``parameters`` is the callable parameter tree, not an instant snapshot.
    Missing forecast years fail explicitly.  Runtime SSA uprating extensions
    supply the household horizon beyond the population scoring window.
    """
    through_year = int(through_year)
    if through_year < 1983:
        raise ValueError("COLA calculations require a benchmark year of 1983 or later")
    try:
        history = parameters("2026-01-01").gov.ssa.social_security.cola
        last_year = int(history.historical_last_effective_year)
        result = []
        for year in range(1975, min(last_year, through_year) + 1):
            # The effective month changed once, in 1983.  Read both dates from
            # parameters so an event never silently receives a January date.
            node = parameters(f"{year}-12-01").gov.ssa.social_security.cola
            effective = f"{year}-{int(node.effective_month_number):02d}"
            payment = f"{year + int(node.first_payment_year_offset)}-{int(node.first_payment_month_number):02d}"
            rule = (
                "dime_floor"
                if int(node.pia_rounding_direction) == -1
                and _decimal(node.pia_rounding_increment) == DIME
                else "unsupported_historical_rounding"
            )
            kwargs = {}
            if year == 1999:
                kwargs = {
                    "as_paid_rate": _decimal(node.december_1999_as_paid_rate),
                    "correction_payment_month": str(
                        int(node.december_1999_correction_payment_month)
                    ),
                }
                kwargs["correction_payment_month"] = (
                    kwargs["correction_payment_month"][:4]
                    + "-"
                    + kwargs["correction_payment_month"][4:]
                )
            result.append(
                ColaEvent(effective, payment, _decimal(node.rate), rule, **kwargs)
            )
        if through_year > last_year + 1:
            # Core parameters carry their final scalar indefinitely.  That is
            # not evidence of a frozen Q3 projection after its last dated
            # observation. Inspect the raw tree, including runtime extensions,
            # before reading instant values that could silently carry forward.
            q3_years = {
                int(observation.instant_str[:4])
                for observation in parameters.gov.ssa.uprating.values_list
                if observation.value is not None
                and observation.instant_str[5:] == "01-01"
            }
            if not q3_years or through_year > max(q3_years):
                horizon = max(q3_years) if q3_years else "unavailable"
                raise ValueError(
                    f"Requested COLA year {through_year} exceeds the frozen Q3 horizon {horizon}"
                )
            # Find the most recent nonzero historical COLA for the high-water
            # anchor.  A zero-COLA year must not reset that comparison basis.
            anchor_year = last_year
            while (
                parameters(f"{anchor_year}-12-01").gov.ssa.social_security.cola.rate
                == 0
            ):
                anchor_year -= 1
            missing_years = set(range(anchor_year + 1, through_year + 1)) - q3_years
            if missing_years:
                raise ValueError(
                    f"The frozen SSA Q3 path is missing payment year {min(missing_years)}"
                )
            q3 = {
                year: _decimal(parameters(f"{year}-01-01").gov.ssa.uprating)
                for year in range(anchor_year + 1, through_year + 1)
            }
            result.extend(
                event
                for event in projected_events(q3)
                if int(event.payment_month[:4]) > last_year + 1
            )
        return tuple(result)
    except (AttributeError, KeyError, TypeError) as error:
        raise ValueError(
            f"No supported SSA COLA/index path through {through_year}"
        ) from error
