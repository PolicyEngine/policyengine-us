"""Shared payment-year decisions for the contributed COLA means test.

Tax returns are read only at y-1 for a January y COLA. Population records use
their supplied/extended prior-year copy; this module never substitutes current
AGI for a missing history. Cohort proxies are resolved within each score year.
"""

from datetime import date
from decimal import Decimal, ROUND_HALF_UP

import numpy as np
from policyengine_core.periods import period as to_period

from policyengine_us.tools.general import has_input_for_period


def indexed_threshold(amount, base_index, current_index, rounding=100):
    """Index a base-dollar line and round half up to the configured dollars."""
    amount, base, current, quantum = map(
        lambda value: Decimal(str(value)),
        (amount, base_index, current_index, rounding),
    )
    if any(not value.is_finite() for value in (amount, base, current, quantum)):
        raise ValueError("Means-test threshold inputs must be finite")
    if amount <= 0 or base <= 0 or current <= 0 or quantum <= 0:
        raise ValueError(
            "Means-test thresholds, CPI levels and rounding must be positive"
        )
    return float(
        (amount * current / base / quantum).quantize(Decimal(1), rounding=ROUND_HALF_UP)
        * quantum
    )


def policy_settings(parameters, payment_year):
    return parameters.gov.contrib.ssa.benefit_levers.cola.means_test(
        f"{int(payment_year):04d}-01-01"
    )


def parameter_choice(value, choices):
    """Decode numeric policy choices supported by Core parameter values."""
    try:
        return choices[value]
    except (KeyError, TypeError) as error:
        raise ValueError(
            f"Unknown COLA means-test parameter choice: {value}"
        ) from error


def policy_active(settings, payment_year):
    if not settings.enabled:
        return False
    if not 1 <= settings.effective_month <= 12:
        raise ValueError("Means-test effective month must lie in [1, 12]")
    # Contemporary COLAs take effect in December and change January checks.
    return (int(payment_year) - 1, 12) >= (
        int(settings.effective_year),
        int(settings.effective_month),
    )


def chained_cola_rates(parameters, through_year):
    """C-CPI-U Q3 rates with A5's high-water, half-up and no-decrease rules.

    Monthly observations are averaged over July--September of the effective
    year. Projected snapshots hold the model's annual index observations; they
    are an explicit projection approximation, not observed monthly forecasts.
    The first available complete Q3 (2000) anchors the payment-2001 series.
    Withholding never changes this index's high-water mark.
    """
    index = parameters.gov.bls.cpi.c_cpi_u
    levels = {}
    for payment_year in range(2001, int(through_year) + 1):
        levels[payment_year] = (
            sum(
                (
                    Decimal(str(index(f"{payment_year - 1}-{month:02d}-01")))
                    for month in (7, 8, 9)
                ),
                Decimal(0),
            )
            / 3
        )
    if any(not level.is_finite() or level <= 0 for level in levels.values()):
        raise ValueError("Chained CPI-U levels must be finite and positive")
    if not levels:
        return {}
    anchor = levels[2001]
    rates = {}
    for year, level in list(levels.items())[1:]:
        rate = max(Decimal(0), level / anchor - 1).quantize(
            Decimal("0.001"), rounding=ROUND_HALF_UP
        )
        rates[year] = float(rate)
        if rate > 0:
            anchor = level
    return rates


def tax_unit_withholding(tax_unit, period, parameters):
    """Income decision before beneficiary-specific cohort/receipt restrictions."""
    year = period.start.year
    p = policy_settings(parameters, year)
    if not policy_active(p, year):
        return False
    sensitivity = parameter_choice(
        p.income_sensitivity,
        {0: "prior_year", 1: "never_withheld", 2: "always_withheld"},
    )
    if sensitivity == "never_withheld":
        return False
    if sensitivity == "always_withheld":
        return True
    previous = period.offset(-1, "year")
    income = tax_unit("social_security_cola_means_test_magi", previous)
    status = tax_unit("filing_status", previous)
    thresholds = p.thresholds
    if thresholds.index_lag < 0:
        raise ValueError("Means-test CPI-U lag must be nonnegative")
    index = parameters.gov.bls.cpi.cpi_u
    base = index(f"{int(thresholds.base_year):04d}-12-01")
    current = index(f"{year - int(thresholds.index_lag):04d}-12-01")
    lines = np.zeros(len(income))
    for filing_status in status.possible_values:
        group = parameter_choice(
            getattr(p.filing_groups, filing_status.name), {0: "single", 1: "joint"}
        )
        line = indexed_threshold(
            getattr(thresholds, group), base, current, thresholds.rounding
        )
        lines = np.where(status == filing_status, line, lines)
    # A9 leaves equality unspecified. Equality receives a COLA by convention.
    return income > lines


def calculator_component_basis(person, period, component):
    """Read selected calculator dates through the calculator's own validation.

    Only the fields used by SuppliedRecord.benchmark are needed here; monetary
    inputs and tax calculations are left to the benefit engine. SurvivorBasis
    retains its ordinary non-WINDEX, disability and exact-date assertions.
    """
    if component not in ("retirement", "survivors"):
        return {}
    from policyengine_us.tools.social_security_benefit_levers import (
        SocialSecurityBenefitSource,
    )

    from .household import SuppliedRecord, SurvivorBasis, month_number

    sources = person(f"social_security_{component}_source", period)
    reported = sources == SocialSecurityBenefitSource.reported
    if np.all(reported):
        return {}
    calculator_sources = person("ss_calculator_source", period)
    allowed = (
        ((SocialSecurityBenefitSource.supplied_ratio_survivor, "survivor"),)
        if component == "survivors"
        else (
            (SocialSecurityBenefitSource.supplied_aime, "aime"),
            (SocialSecurityBenefitSource.supplied_pia, "pia"),
        )
    )
    results = {}
    for index in np.flatnonzero(~reported):
        source = str(calculator_sources[index])
        if not any(
            sources[index] == selector.index and source == mode
            for selector, mode in allowed
        ):
            raise ValueError(
                "Public Social Security source must match the supported ss_calculator_source"
            )

        def value(name):
            scalar = person("ss_calculator_" + name, period)[index]
            return scalar.item() if hasattr(scalar, "item") else scalar

        def optional_date(name):
            text = str(value(name))
            return date.fromisoformat(text) if text else None

        survivor = None
        if source == "survivor":
            prior_disability = value("prior_disability_eligibility")
            if prior_disability not in (0, 1):
                raise ValueError(
                    "ss_calculator_prior_disability_eligibility must explicitly "
                    "be 0 (no prior eligibility) or 1 (prior disability eligibility)"
                )
            same_year = int(value("same_year_death_before_62"))
            if same_year not in (-1, 0, 1):
                raise ValueError("Same-year death assertion must be -1, 0 or 1")
            survivor = SurvivorBasis(
                worker_birth_year=int(value("worker_birth_year")),
                death_year=int(value("death_year")),
                provenance=str(value("basis_provenance")),
                worker_birth_date=optional_date("worker_birth_date"),
                death_date=optional_date("death_date"),
                authoritative_year=int(value("authoritative_year")) or None,
                prior_disability_eligibility=bool(prior_disability),
                ordinary_non_windex=bool(value("ordinary_non_windex")),
                year_only_not_january_1=bool(value("year_only_not_january_1")),
                same_year_death_before_62=None if same_year == -1 else bool(same_year),
            )
        record = SuppliedRecord(
            source=source,
            worker_id=str(value("worker_id")),
            birth_date=date.fromisoformat(str(value("birth_date"))),
            entitlement_month=str(value("entitlement_month")),
            insured=bool(value("insured")),
            eligibility_year=int(value("eligibility_year")) or None,
            source_basis=str(value("source_basis")),
            survivor=survivor,
        )
        benchmark = record.benchmark()
        check_year, check_month = divmod(month_number(record.entitlement_month) + 1, 12)
        results[index] = benchmark, check_year, check_month + 1
    return results


def component_eligibility_year(person, period, component):
    """Resolve supplied worker links before the documented cross-section proxy."""
    calculated = calculator_component_basis(person, period, component)
    prefix = f"social_security_{component}"
    eligibility = person(f"{prefix}_worker_eligibility_year", period).copy()
    links = person(f"{prefix}_worker_id", period)
    shared = person("social_security_worker_computation_year", period)
    known = {str(identifier): i for i, identifier in enumerate(person.ids)}
    for index, link in enumerate(links):
        if index in calculated or not link:
            continue
        if str(link) not in known:
            raise ValueError("Social Security worker_id does not identify a person")
        other = known[str(link)]
        linked = eligibility[other] or shared[other]
        if eligibility[index] and linked and eligibility[index] != linked:
            raise ValueError("Conflicting supplied and linked worker computation years")
        eligibility[index] = eligibility[index] or linked
    year = period.start.year
    age = person("age", period)
    entitlement = person(f"{prefix}_entitlement_year", period)
    if component == "retirement":
        proxy = year - age + 62
    elif component == "survivors":
        proxy = np.where(age >= 60, year - age + 60, 1975)
    else:
        proxy = np.where(entitlement > 0, entitlement, 1975)
    result = np.where(eligibility > 0, eligibility, proxy)
    for index, (benchmark, _, _) in calculated.items():
        result[index] = benchmark
    return result


def component_receipt_year(person, period, component):
    prefix = f"social_security_{component}"
    entitlement = person(f"{prefix}_entitlement_year", period)
    month = person(f"{prefix}_entitlement_month", period)
    # Unknown receipt dates use already-in-payment exposure, as A5 does.
    result = np.where(entitlement > 0, entitlement + (month == 12), 0)
    for index, (_, check_year, _) in calculator_component_basis(
        person, period, component
    ).items():
        result[index] = check_year
    return result


def component_receipt_month(person, period, component):
    """First check month following the supplied entitlement month."""
    prefix = f"social_security_{component}"
    entitlement = person(f"{prefix}_entitlement_year", period)
    month = person(f"{prefix}_entitlement_month", period)
    if np.any((entitlement > 0) & ((month < 1) | (month > 12))):
        raise ValueError("Social Security entitlement months must lie in [1, 12]")
    result = np.where(entitlement > 0, month % 12 + 1, 1)
    for index, (_, _, check_month) in calculator_component_basis(
        person, period, component
    ).items():
        result[index] = check_month
    return result


def before_receipt(payment_year, receipt_year, receipt_month):
    """Whether a January COLA check event precedes the first benefit check."""
    return (payment_year < receipt_year) | (
        (payment_year == receipt_year) & (1 < receipt_month)
    )


def cohort_mask(settings, eligibility_year):
    scope = parameter_choice(
        settings.scope, {0: "first_eligible_cohorts", 1: "all_beneficiaries"}
    )
    if scope == "all_beneficiaries":
        return np.ones_like(eligibility_year, dtype=bool)
    return np.asarray(eligibility_year) >= settings.first_eligible_year


def cola_override(person, name, period):
    """Read an exact-year tri-state input without carrying past overrides."""
    if not has_input_for_period(person.simulation, name, period):
        return np.full(len(person.ids), -1, dtype=int)
    override = person(name, period)
    if np.any(~np.isin(override, (-1, 0, 1))):
        raise ValueError("COLA override must be -1 (auto), 0 (paid), or 1 (withheld)")
    return override


def component_withholding(
    person,
    period,
    parameters,
    component,
    eligibility_year=None,
    receipt_year=None,
    receipt_month=None,
    use_explicit=False,
):
    """Apply the TaxUnit decision to this beneficiary and payment event.

    The reported-factor caller supplies its score-year eligibility proxy for
    every historical event. It does not re-age a static row within one score.
    E3 overrides are separate tri-state inputs, so an omitted person remains
    automatic even when another person's decision is supplied. The legacy
    boolean input remains A5's channel when E3 is disabled.
    """
    period = to_period(period)
    year = period.start.year
    p = policy_settings(parameters, year)
    if not p.enabled:
        return person(f"social_security_{component}_cola_withheld", period)
    override = cola_override(
        person, f"social_security_{component}_cola_override", period
    )
    if not policy_active(p, year) or np.all(override != -1):
        return override == 1
    eligibility_year = (
        component_eligibility_year(person, period, component)
        if eligibility_year is None
        else np.asarray(eligibility_year)
    )
    receipt_year = (
        component_receipt_year(person, period, component)
        if receipt_year is None
        else np.asarray(receipt_year)
    )
    receipt_month = (
        component_receipt_month(person, period, component)
        if receipt_month is None
        else np.asarray(receipt_month)
    )
    eligible = (
        cohort_mask(p, eligibility_year)
        & ~before_receipt(year, receipt_year, receipt_month)
        & (override == -1)
    )
    if not np.any(eligible):
        return override == 1
    return (override == 1) | (
        eligible & person.tax_unit("social_security_cola_means_test_withheld", period)
    )


def indexed_cola_rate(
    person,
    reference_period,
    parameters,
    component,
    payment_year,
    baseline_rate,
    eligibility_year=None,
    receipt_year=None,
    receipt_month=None,
):
    """Select the below-line or pre-receipt index before A5's policy addition."""
    p = policy_settings(parameters, payment_year)
    if not policy_active(p, payment_year):
        return baseline_rate
    eligibility_year = (
        component_eligibility_year(person, reference_period, component)
        if eligibility_year is None
        else np.asarray(eligibility_year)
    )
    receipt_year = (
        component_receipt_year(person, reference_period, component)
        if receipt_year is None
        else np.asarray(receipt_year)
    )
    receipt_month = (
        component_receipt_month(person, reference_period, component)
        if receipt_month is None
        else np.asarray(receipt_month)
    )
    below = parameter_choice(
        p.below_threshold_cola_index, {0: "statutory", 1: "chained_cpi_u"}
    )
    before = parameter_choice(
        p.pre_receipt_cola_index,
        {-1: "follow_below_threshold", 0: "statutory", 1: "chained_cpi_u"},
    )
    if before == "follow_below_threshold":
        before = below
    chained = cohort_mask(p, eligibility_year) & np.where(
        before_receipt(payment_year, receipt_year, receipt_month),
        before == "chained_cpi_u",
        below == "chained_cpi_u",
    )
    if not np.any(chained):
        return baseline_rate
    rates = chained_cola_rates(parameters, payment_year)
    if payment_year not in rates:
        raise ValueError("Chained CPI-U COLAs require payment year 2002 or later")
    return np.where(chained, rates[payment_year], baseline_rate)
