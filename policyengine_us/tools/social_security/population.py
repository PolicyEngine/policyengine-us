"""Reported-benefit PIA inference for independent annual cross-sections.

Only unreformed reported inputs enter this adapter. Calculated sources already
read the shared formula path themselves and bypass the population ratio. Annual
survey amounts are treated as full-year gross benefits; their PIA intervals are
conditional diagnostics, not identified monthly-payment histories.
"""

from datetime import date
from decimal import Decimal
from fractions import Fraction

import numpy as np

from policyengine_us.tools.social_security.cola import (
    cola_factor,
    read_parameter_events,
)
from policyengine_us.tools.social_security.household import (
    attainment_month,
    claiming_factor,
    full_retirement_age_months,
    month_string,
)
from policyengine_us.tools.social_security.parameters import (
    bend_points_at,
    formula_path_at,
)
from policyengine_us.tools.social_security.pia import has_active_reform
from policyengine_us.tools.social_security.pia_ratio import compute_pia_ratio
from policyengine_us.tools.social_security.records import resolve_worker_basis
from policyengine_us.tools.social_security.population_survivor import (
    survivor_formula_path,
)
from policyengine_us.tools.social_security_benefit_levers import (
    SocialSecurityBenefitSource,
)
from policyengine_us.tools.period_branch import has_input


SCENARIOS = {
    "supplied_claim_age",
    "entitlement_dates",
    "age_62",
    "age_65",
    "fra",
    "age_70",
}


def _choice(value):
    # Core supports lists but not scalar strings. Retain readable named
    # scenarios without adding another policy-selection mechanism.
    if isinstance(value, (list, tuple, np.ndarray)) and len(value) == 1:
        value = value[0]
    if not isinstance(value, str):
        raise ValueError("A PIA-ratio scenario must contain exactly one name")
    return value


def _disability_proxy_year(parameters, year, scenario):
    if scenario == "current_year":
        return year
    if scenario != "pre_reform":
        raise ValueError("Choose pre_reform or current_year for disability eligibility")
    # This is an exposure sensitivity, not an observed onset distribution.
    # Use the cohort immediately before the first enabled formula change.
    starts = [year]
    node = parameters.gov.contrib.ssa.pia
    for entry in node.in_effect.values_list:
        if entry.value and int(entry.instant_str[:4]) <= year:
            starts.append(int(entry.instant_str[:4]))
    for entry in parameters.gov.contrib.congress.s770.section_2.in_effect.values_list:
        if entry.value and int(entry.instant_str[:4]) <= year:
            starts.append(max(2026, int(entry.instant_str[:4])))
    return max(1983, min(starts) - 1)


def _record_basis(person, period, parameters, component):
    """Resolve supplied record information before any labelled age proxy."""
    prefix = f"social_security_{component}"
    year = period.start.year
    amounts = person(f"{prefix}_reported", period)
    reported = (
        person(f"{prefix}_source", period) == SocialSecurityBenefitSource.reported
    )
    if np.any(reported & (~np.isfinite(amounts) | (amounts < 0))):
        raise ValueError(
            "Reported Social Security benefits must be finite and nonnegative"
        )
    positive = reported & (amounts > 0)
    n = len(amounts)
    if not np.any(positive):
        return dict(
            amounts=amounts,
            positive=positive,
            eligibility_year=np.zeros(n, dtype=int),
            claiming_adjustment=[Fraction(1)] * n,
            shares=[Fraction(1)] * n,
            own_record_retired_worker=np.zeros(n, dtype=bool),
            missing_claim_age=np.zeros(n, dtype=bool),
            pre_1983=np.zeros(n, dtype=bool),
            unmodeled=np.zeros(n, dtype=bool),
            proxy=np.zeros(n, dtype=bool),
            measurement_uncertainty=np.zeros(n, dtype=bool),
            survivor_paths={},
        )
    age = person("age", period)
    birth_years = person("birth_year", period)
    supplied_birth_year = has_input(person.simulation, "birth_year", period)
    years, linked, worker_indices = resolve_worker_basis(
        person, period, component, positive
    )
    supplied = years > 0
    entitlement = person(f"{prefix}_entitlement_year", period)
    proxy = np.zeros(n, dtype=bool)
    missing_claim_age = np.zeros(n, dtype=bool)
    unmodeled = np.zeros(n, dtype=bool)
    own = np.zeros(n, dtype=bool)
    adjustments = [Fraction(1)] * n
    shares = [Fraction(1)] * n
    policy = parameters.gov.contrib.ssa.benefit_levers.pia_ratio(period.start)

    if component == "retirement":
        for i in np.flatnonzero(positive):
            adjustments[i] = Fraction(
                0
            )  # Unknown until the selected scenario is usable.
        # An entitlement date is a claim date, not age-62 eligibility. In its
        # absence the scoring year's age rebuilds the cohort independently.
        # A link without an explicit computation basis is not permission to
        # infer an unrelated worker's record from the recipient's age.
        unmodeled |= linked & ~supplied
        own = positive & (age >= 62) & (worker_indices == np.arange(n))
        mixed = np.zeros(n, dtype=bool)
        for other in ("survivors", "dependents", "disability"):
            mixed |= person(f"social_security_{other}_reported", period) > 0
        own &= ~mixed
        # Mixed recipient components do not establish a separable own-worker
        # PIA in the presence of dual entitlement or partial-year conversions.
        unmodeled |= positive & mixed
        scenario = _choice(policy.claiming_scenario)
        if scenario not in SCENARIOS:
            raise ValueError("Unsupported PIA-ratio claiming_scenario")
        months = person("social_security_retirement_claim_age_months", period)
        birth_months = person("social_security_birth_month", period)
        birth_days = person("social_security_birth_day", period)
        birth_dates = person("ss_calculator_birth_date", period)
        entitlement_months = person(f"{prefix}_entitlement_month", period)
        births = [None] * n
        exact_births = np.zeros(n, dtype=bool)
        known_birth_months = np.zeros(n, dtype=bool)
        for i in np.flatnonzero(positive):
            j = worker_indices[i]
            known_birth_year = supplied_birth_year and birth_years[j] > 0
            cohort = (
                int(birth_years[j])
                if known_birth_year
                else int(years[i]) - 62
                if supplied[i]
                else year - int(age[j])
            )
            observed_birth_month = None
            if (
                not known_birth_year
                and not str(birth_dates[j])
                and entitlement[i] > 0
                and 744 <= months[i] <= 840
            ):
                if not 1 <= entitlement_months[i] <= 12:
                    raise ValueError(
                        "Social Security entitlement month must lie in [1, 12]"
                    )
                observed_birth_month = (
                    int(entitlement[i]) * 12
                    + int(entitlement_months[i])
                    - 1
                    - int(months[i])
                )
                cohort = observed_birth_month // 12
            birth = date(cohort, 1, 2)
            exact_birth = False
            if str(birth_dates[j]):
                birth = date.fromisoformat(str(birth_dates[j]))
                exact_birth = True
                known_birth_months[i] = True
            elif birth_months[j]:
                try:
                    birth = date(cohort, int(birth_months[j]), int(birth_days[j]) or 2)
                except ValueError as error:
                    raise ValueError(
                        "Invalid Social Security birth month/day"
                    ) from error
                exact_birth = bool(birth_days[j])
                known_birth_months[i] = True
            elif observed_birth_month is not None:
                birth = date(cohort, observed_birth_month % 12 + 1, 2)
            births[i], exact_births[i] = birth, exact_birth
            if not supplied[i] and not linked[i]:
                if exact_birth:
                    years[i] = attainment_month(birth, 744) // 12
                elif known_birth_year:
                    years[i] = birth.year + 62
                    proxy[i] = True
                elif observed_birth_month is not None:
                    # Only observed claim age identifies this cohort. Changing
                    # the sensitivity for a must not change the worker's E.
                    years[i] = (observed_birth_month + 744) // 12
                    proxy[i] = True
            if not years[i]:
                years[i] = year - age[i] + 62
                proxy[i] = True
        for i in np.flatnonzero(positive & (years >= 1983)):
            birth = births[i]
            exact_birth = exact_births[i]
            if not exact_birth:
                proxy[i] = True
            if scenario == "entitlement_dates":
                if not known_birth_months[i] or entitlement[i] <= 0:
                    missing_claim_age[i] = True
                    continue
                if not 1 <= entitlement_months[i] <= 12:
                    raise ValueError(
                        "Social Security entitlement month must lie in [1, 12]"
                    )
                claim = int(entitlement[i]) * 12 + int(entitlement_months[i]) - 1
                claim_months = claim - attainment_month(birth, 0)
            else:
                claim_months = {
                    "supplied_claim_age": int(months[i]),
                    "age_62": 744,
                    "age_65": 780,
                    "fra": full_retirement_age_months(birth),
                    "age_70": 840,
                }[scenario]
                claim = attainment_month(birth, claim_months)
            if not 744 <= claim_months <= 840:
                missing_claim_age[i] = True
                continue
            # The annual in-payment approximation uses fully credited DRCs.
            # Partial entitlement years/deferred same-year credits require the
            # household monthly ledger rather than annual survey inversion.
            adjustments[i] = claiming_factor(
                birth, month_string(claim), month_string((claim // 12 + 1) * 12)
            )
    elif component == "disability":
        years = np.where(years > 0, years, entitlement)
        missing = years <= 0
        years = np.where(
            missing,
            _disability_proxy_year(
                parameters, year, _choice(policy.disability_eligibility_proxy)
            ),
            years,
        )
        proxy |= missing
    else:
        # A worker link/year and an identified composite a*s are both needed.
        # No auxiliary inversion ever substitutes the recipient's age.
        ratio = person(f"{prefix}_worker_benefit_ratio", period)
        identified = person(f"{prefix}_worker_ratio_identified", period)
        if np.any(positive & identified & (~np.isfinite(ratio) | (ratio <= 0))):
            raise ValueError(
                "An identified worker benefit ratio must be positive and finite"
            )
        unmodeled |= ~(linked & supplied & identified)
        for i in np.flatnonzero(positive & ~unmodeled):
            shares[i] = Fraction(str(ratio[i]))

    if np.any(positive & supplied & (years > year)):
        raise ValueError("Social Security eligibility cannot follow the scoring year")
    unmodeled |= positive & (years > year)
    pre1983 = positive & (years > 0) & (years < 1983)
    unmodeled = positive & (unmodeled | missing_claim_age | pre1983)
    survivor_paths = {}
    if component == "survivors":
        for i in np.flatnonzero(positive & ~unmodeled):
            path, mode = formula_path_at(parameters, int(years[i]), year)
            path, unsupported = survivor_formula_path(
                person, period, parameters, i, path, int(years[i]), worker_indices[i]
            )
            unmodeled[i] |= unsupported
            survivor_paths[i] = (path, mode)
    return dict(
        amounts=amounts,
        positive=positive,
        eligibility_year=np.where(positive, years, 0),
        claiming_adjustment=adjustments,
        shares=shares,
        own_record_retired_worker=own,
        missing_claim_age=positive & missing_claim_age,
        pre_1983=pre1983,
        unmodeled=unmodeled,
        proxy=positive & proxy,
        measurement_uncertainty=positive & ~unmodeled,
        survivor_paths=survivor_paths,
    )


def reported_pia_ratio_output(person, period, parameters, component, field):
    """Named Person diagnostics and factor using one unreformed source basis."""
    if field == "factor":
        year = period.start.year
        custom = any(
            entry.value and int(entry.instant_str[:4]) <= year
            for entry in parameters.gov.contrib.ssa.pia.in_effect.values_list
        )
        s770 = parameters.gov.contrib.congress.s770.section_2(period.start).in_effect
        if not custom and not s770:
            # Neutral current law must not require newly supplied record fields.
            # This also preserves legacy amounts for records outside C's scope.
            amount = person(f"social_security_{component}_reported", period)
            reported = (
                person(f"social_security_{component}_source", period)
                == SocialSecurityBenefitSource.reported
            )
            if np.any(reported & (~np.isfinite(amount) | (amount < 0))):
                raise ValueError(
                    "Reported Social Security benefits must be finite and nonnegative"
                )
            return np.ones(len(amount))
    basis = _record_basis(person, period, parameters, component)
    if field in basis and field != "claiming_adjustment":
        return basis[field]
    if field == "claiming_adjustment":
        return np.array([float(value) for value in basis[field]])
    if field not in ("factor", "aime", "aime_lower", "aime_upper"):
        raise ValueError("Unknown reported PIA ratio output")
    result = (
        np.ones(len(basis["amounts"]))
        if field == "factor"
        else np.zeros(len(basis["amounts"]))
    )
    supported = basis["positive"] & ~basis["unmodeled"]
    if not np.any(supported):
        return result
    year = period.start.year
    paths = {}
    for eligibility in np.unique(basis["eligibility_year"][supported]):
        eligibility = int(eligibility)
        path, mode = formula_path_at(parameters, eligibility, year)
        paths[eligibility] = (path, mode)
    if field == "factor" and not any(
        has_active_reform(path, eligibility, year, mode)
        for eligibility, (path, mode) in paths.items()
    ):
        return result
    events = read_parameter_events(parameters, year)
    cola_by_year = {}
    bends_by_year = {}
    bound = parameters.gov.contrib.ssa.benefit_levers.pia_ratio(
        period.start
    ).annual_rounding_bound
    for i in np.flatnonzero(supported):
        eligibility = int(basis["eligibility_year"][i])
        if eligibility not in cola_by_year:
            cola_by_year[eligibility] = cola_factor(eligibility, f"{year}-12", events)
            bends_by_year[eligibility] = bend_points_at(parameters, eligibility)
        path, mode = basis["survivor_paths"].get(i, paths[eligibility])
        # The shortest decimal representation of Core's float32 input restores
        # ordinary supplied cents without expanding binary noise into a PIA dime.
        amount = Decimal(str(basis["amounts"][i]))
        inference = compute_pia_ratio(
            amount,
            eligibility,
            path,
            year,
            mode,
            bend_points=bends_by_year[eligibility],
            claiming_adjustment=basis["claiming_adjustment"][i],
            auxiliary_share=basis["shares"][i],
            cola_factor=cola_by_year[eligibility],
            annual_rounding_bound=bound,
        )
        value = getattr(inference, field)
        if field == "factor":
            value = np.float32(value)
        else:
            # A nearest-rounded float32 inverse may lie below its exact
            # endpoint and lose a PIA dime. Preserve a representable ceiling.
            represented = np.float32(value)
            if (
                np.isfinite(represented)
                and Decimal.from_float(float(represented)) < value
            ):
                represented = np.nextafter(represented, np.float32(np.inf))
            value = represented
        if not np.isfinite(float(value)):
            raise ValueError("PIA ratio output exceeds the supported numeric range")
        result[i] = float(value)
    return result
