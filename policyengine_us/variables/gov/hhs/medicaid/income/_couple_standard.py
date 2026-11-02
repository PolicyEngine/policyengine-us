from policyengine_us.model_api import *


def spouses_split_by_facility(person: Population, period: Period) -> ArrayLike:
    # 20 CFR 416.414(b)(3): SSI computes each spouse separately when a facility
    # splits a couple who are both aged, blind or disabled.
    return person("ssi_claim_is_joint", period) & ~person(
        "ssi_couple_computation_applies", period.first_month
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
    # their own, so stays with the couple.
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
