"""Payment-event algebra and the reported Social Security benefit route.

This module never derives COLAs from benefit-income uprating. Historical events
are statutory rates; projections use the system's January-keyed Q3 schedule.
"""

from decimal import Decimal, ROUND_HALF_UP

import numpy as np
from policyengine_core.model_api import Enum

from policyengine_us.tools.social_security.records import resolve_worker_basis
from policyengine_us.tools.ssa_cola_history import validate_cola_rounding_rule


class SocialSecurityBenefitSource(Enum):
    reported = "Reported benefits"
    supplied_aime = "Supplied eligibility-level AIME"
    supplied_pia = "Supplied unreformed eligibility-level PIA"
    supplied_ratio_survivor = "Supplied-ratio survivor calculation"
    history = "Annual earnings history"


class SocialSecurityFund(Enum):
    unspecified = "Underlying trust fund not supplied"
    oasi = "Old-Age and Survivors Insurance"
    di = "Disability Insurance"


def projected_cola_rates(indices):
    """Return statutory rates after the first (anchor) January index year.

    A zero rounded increase does not reset the last effective COLA's Q3 base.
    """
    years = sorted(indices)
    if not years:
        return {}
    high_water = Decimal(str(indices[years[0]]))
    if not high_water.is_finite() or high_water <= 0:
        raise ValueError("SSA Q3 index levels must be finite and positive")
    rates = {}
    for year in years[1:]:
        index = Decimal(str(indices[year]))
        if not index.is_finite() or index <= 0:
            raise ValueError("SSA Q3 index levels must be finite and positive")
        rate = max(Decimal(0), index / high_water - 1).quantize(
            Decimal("0.001"), rounding=ROUND_HALF_UP
        )
        rates[year] = float(rate)
        if rate > 0:
            high_water = index
    return rates


def joint_cola_factor(events, first_payment, through_year, pp_changes, withheld):
    """One numerator per exposed event, including the withholding decision.

    Annual reported amounts use the payment-calendar-year convention. First
    payment month distinguishes the historical July events from January checks.
    This ratio is a population approximation, not a reconstructed rounded PIA.
    """
    factor = 1.0
    for event in events:
        year, month = event["payment_year"], event["payment_month"]
        if (year, month) < first_payment or year > through_year:
            continue
        validate_cola_rounding_rule(event["rounding_rule"])
        rate = float(event["rate"])
        delta = float(pp_changes.get(year, 0))
        factor *= cola_event_multiplier(rate, delta, withheld.get(year, False))
    return float(factor)


def cola_event_multiplier(rate, delta, withheld):
    """Shared scalar/vector algebra for an exposed payment event."""
    if not np.isfinite(rate) or rate < 0 or not np.isfinite(delta):
        raise ValueError("COLA rates must be nonnegative and changes finite")
    numerator = np.where(withheld, 1, 1 + max(0, rate + delta))
    return numerator / (1 + rate)


def cola_events(parameters, through_year):
    """Export the exact historical and projected payment-event schedule used."""
    history = parameters.gov.ssa.cola_history
    events = []
    for entry in reversed(history.rate.values_list):
        instant = entry.instant_str
        p = history(instant)
        effective_year = int(instant[:4])
        payment_year = effective_year + (p.effective_month == 12)
        events.append(
            dict(
                effective_date=instant,
                payment_year=int(payment_year),
                payment_month=int(p.first_payment_month),
                rate=float(entry.value),
                rounding_rule=int(p.pia_rounding),
                source="historical",
            )
        )
    last_actual = max(e["payment_year"] for e in events)
    if through_year > last_actual:
        indices = {
            year: parameters(f"{year}-01-01").gov.ssa.uprating
            for year in range(last_actual, through_year + 1)
        }
        for year, rate in projected_cola_rates(indices).items():
            events.append(
                dict(
                    effective_date=f"{year - 1}-12-01",
                    payment_year=year,
                    payment_month=1,
                    rate=rate,
                    rounding_rule=2,
                    source="gov.ssa.uprating",
                )
            )
    return sorted(
        (e for e in events if e["payment_year"] <= through_year),
        key=lambda e: (e["payment_year"], e["payment_month"]),
    )


def selected_reported_benefit(person, period, component):
    prefix = f"social_security_{component}"
    source = person(f"{prefix}_source", period)
    if np.any(source != SocialSecurityBenefitSource.reported):
        raise NotImplementedError(
            "Calculated Social Security source modes are reserved; "
            "this implementation supports the reported route only"
        )
    return person(f"{prefix}_reported", period)


def reported_joint_cola_factor(person, period, parameters, component):
    prefix = f"social_security_{component}"
    reported = (
        person(f"{prefix}_source", period) == SocialSecurityBenefitSource.reported
    )
    if not np.any(reported):
        return 1
    year = period.start.year
    p = parameters(period).gov.contrib.ssa.benefit_levers.cola
    if not 1 <= p.effective_month <= 12:
        raise ValueError("COLA effective month must lie in [1, 12]")
    raw_policy = parameters.gov.contrib.ssa.benefit_levers.cola
    # An earlier withheld or adjusted COLA remains in the payment level after
    # a policy is switched off. Inspect the parameter history, not just today.
    active = any(
        entry.instant_str <= f"{year}-12-31"
        and (entry.value >= 0 if name == "alternative_rate" else bool(entry.value))
        for name in ("withholding_enabled", "pp_change", "alternative_rate")
        for entry in getattr(raw_policy, name).values_list
    )
    if not active:
        return 1
    events = cola_events(parameters, year)
    first_year = person(f"{prefix}_first_cola_year", period)
    first_month = person(f"{prefix}_first_cola_month", period)
    entitlement_month = person(f"{prefix}_entitlement_month", period)
    if np.any(reported & ((first_month < 1) | (first_month > 12))) or np.any(
        reported & ((entitlement_month < 1) | (entitlement_month > 12))
    ):
        raise ValueError("Social Security input months must lie in [1, 12]")
    # Links follow an explicitly supplied record basis, never a recipient-age
    # retirement assumption on an auxiliary/disability record.
    worker_year, linked, _ = resolve_worker_basis(person, period, component, reported)
    if np.any(reported & linked & (worker_year == 0) & (first_year <= 0)):
        raise ValueError("Linked worker requires an explicit eligibility year")
    entitlement = person(f"{prefix}_entitlement_year", period)
    age = person("age", period)
    if component == "retirement":
        eligibility = year - age + 62
        proxy = eligibility + (eligibility >= 1983)
    elif component == "survivors":
        eligibility = year - age + 60
        proxy = np.where(age >= 60, eligibility + (eligibility >= 1983), 1975)
    else:
        proxy = np.full(len(age), 1975)
    # Modern December COLAs first reach January checks in the next year.
    # For supplied historical entitlement dates, June-effective events are
    # included only once the recipient was entitled by that effective month.
    historical_first = np.where(
        (entitlement > 0) & (entitlement <= 1982),
        entitlement + (entitlement_month > 6),
        entitlement + 1,
    )
    # A retirement entitlement date can be a late claim. It must not discard
    # the COLAs accrued since eligibility at 62.
    recipient_origin = (
        proxy
        if component == "retirement"
        else np.where(entitlement > 0, historical_first, proxy)
    )
    inferred = np.where(
        worker_year > 0,
        worker_year + (worker_year >= 1983),
        recipient_origin,
    )
    first_year = np.where(first_year > 0, first_year, inferred)
    result = np.ones(len(age))
    for event in events:
        payment_year, month = event["payment_year"], event["payment_month"]
        exposed = (first_year < payment_year) | (
            (first_year == payment_year) & (first_month <= month)
        )
        exposed &= reported
        if not np.any(exposed):
            continue
        validate_cola_rounding_rule(event["rounding_rule"])
        policy = parameters(f"{payment_year}-01-01").gov.contrib.ssa.benefit_levers.cola
        effective = event["effective_date"]
        applies = (
            (
                effective
                >= f"{int(policy.effective_year):04d}-{int(policy.effective_month):02d}-01"
            )
            if policy.effective_year
            else payment_year >= policy.start_year
        )
        applies &= not policy.end_year or payment_year <= policy.end_year
        baseline = event["rate"]
        alternative = policy.alternative_rate
        if (
            not np.isfinite(policy.pp_change)
            or not np.isfinite(alternative)
            or (alternative < 0 and alternative != -1)
        ):
            raise ValueError(
                "COLA change must be finite; alternative rate must be nonnegative or -1"
            )
        rate = (
            (alternative if alternative >= 0 else baseline) + policy.pp_change
            if applies
            else baseline
        )
        withheld = (
            person(f"{prefix}_cola_withheld", payment_year)
            if policy.withholding_enabled
            else False
        )
        multiplier = cola_event_multiplier(baseline, rate - baseline, withheld)
        result *= np.where(exposed, multiplier, 1)
    return result
