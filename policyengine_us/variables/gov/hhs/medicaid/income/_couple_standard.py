from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_budget_total,
    _ssi_couple_total,
    _ssi_spouse_index,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


def in_married_couple(person: Population, period: Period) -> ArrayLike:
    # A two-person marital unit is a married couple. A larger unit is the default
    # group of a situation that omits marital units, where the SSI spouse test
    # finds the couple.
    return (person.marital_unit.nb_persons() == 2) | (
        _ssi_spouse_index(person, period) >= 0
    )


def spouses_sum(person: Population, period: Period, values: ArrayLike) -> ArrayLike:
    # A person's value plus their spouse's. A default marital unit of more than
    # two people holds others too, who stay out.
    marital_unit = person.marital_unit
    return where(
        marital_unit.nb_persons() > 2,
        _ssi_couple_total(person, period, values),
        marital_unit.sum(values),
    )


def couple_budget_total(
    person: Population, period: Period, values: ArrayLike
) -> ArrayLike:
    # Both spouses' values, plus their dependents' under SSI's couple
    # computation, as a spend-down budget totals a couple. An unrelated member
    # of a default marital unit stays out, and that member's own total leaves
    # out the couple.
    return where(
        person("ssi_couple_computation_applies", period),
        _ssi_couple_budget_total(person, period, values),
        _ssi_couple_total(person, period, values),
    )


def spouses_split_by_facility(person: Population, period: Period) -> ArrayLike:
    # Exactly one member of a married couple is in a Medicaid-paid facility. SSI
    # computes each member of an eligible couple separately (20 CFR 416.414(b)(3)).
    # For any institutionalized spouse (42 USC 1396r-5(h)(1)), "no income of the
    # community spouse shall be deemed available to the institutionalized spouse"
    # (42 USC 1396r-5(b)(1)), and that section supersedes any inconsistent Medicaid
    # provision ((a)(1)). Core reads this month-defined stock at a year's last month,
    # as income reads ssi_couple_computation_applies, so both agree on a part-year
    # stay.
    in_facility = (
        person("ssi_federal_living_arrangement", period)
        == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY
    )
    return in_married_couple(person, period) & (
        spouses_sum(person, period, in_facility) == 1
    )


def uses_couple_standard(
    person: Population,
    period: Period,
    budgets_together: ArrayLike,
    couple_limit_without_deeming: ArrayLike,
) -> ArrayLike:
    # Under SSI's rule an applicant with an ineligible spouse is tested alone
    # unless the spouse's income is deemed (20 CFR 416.1163(d)). States may
    # instead budget the couple together, or keep the couple standard without
    # deeming. A person with no aged, blind or disabled status has no test of
    # their own, so stays with the couple. A couple split by a facility is never
    # tested together.
    is_married = in_married_couple(person, period)
    aged_blind_disabled = person("is_ssi_aged_blind_disabled", period)
    has_ineligible_spouse = (
        aged_blind_disabled
        & is_married
        & (spouses_sum(person, period, aged_blind_disabled) == 1)
    )
    nothing_deemed = ~person("is_ssi_spousal_deeming_applies", period)
    tested_alone = has_ineligible_spouse & nothing_deemed
    return (
        is_married
        & ~spouses_split_by_facility(person, period)
        & (budgets_together | couple_limit_without_deeming | ~tested_alone)
    )
