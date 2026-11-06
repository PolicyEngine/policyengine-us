from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
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
    marital_unit = person.marital_unit
    in_facility = (
        person("ssi_federal_living_arrangement", period)
        == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY
    )
    return (marital_unit.nb_persons() == 2) & (marital_unit.sum(in_facility) == 1)


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
    marital_unit = person.marital_unit
    is_married = marital_unit.nb_persons() == 2
    aged_blind_disabled = person("is_ssi_aged_blind_disabled", period)
    has_ineligible_spouse = (
        aged_blind_disabled & is_married & (marital_unit.sum(aged_blind_disabled) == 1)
    )
    nothing_deemed = ~person("is_ssi_spousal_deeming_applies", period)
    tested_alone = has_ineligible_spouse & nothing_deemed
    return (
        is_married
        & ~spouses_split_by_facility(person, period)
        & (budgets_together | couple_limit_without_deeming | ~tested_alone)
    )
