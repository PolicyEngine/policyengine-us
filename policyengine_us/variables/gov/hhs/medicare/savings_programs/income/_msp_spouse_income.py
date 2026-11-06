from policyengine_us.model_api import *


def msp_spouse_value(values: ArrayLike, spouse: ArrayLike) -> ArrayLike:
    # Each person's spouse's value, or zero for a person with no spouse. The
    # spouse is the row from _ssi_spouse_index, not the rest of the marital unit,
    # because a situation that omits marital units puts everyone in one.
    return values[np.maximum(spouse, 0)] * (spouse >= 0)


def msp_spouses_combine_income(
    person: Population, period: Period, spouse: ArrayLike
) -> ArrayLike:
    # Spouses who are both on Medicare are tested together. So is an eligible
    # couple: each spouse must be eligible for SSI (20 CFR 416.1801(c); POMS SI
    # 00501.154 A.1), not only aged, blind or disabled, and uncapped_ssi above
    # zero adds the income test that is_ssi_eligible leaves out.
    is_medicare_eligible = person("is_medicare_eligible", period.this_year)
    both_on_medicare = is_medicare_eligible & msp_spouse_value(
        is_medicare_eligible, spouse
    )
    eligible_for_ssi = person("uncapped_ssi", period) > 0
    eligible_couple = (
        person("ssi_couple_computation_applies", period)
        & eligible_for_ssi
        & msp_spouse_value(eligible_for_ssi, spouse)
    )
    return both_on_medicare | eligible_couple


def msp_spouse_income(person: Population, year: Period, spouse: ArrayLike) -> tuple:
    # A spouse's annual earned and unearned income after allocations for
    # ineligible children, which come off unearned income first (20 CFR
    # 416.1163(a) and (b)). Any spouse who is not eligible for SSI is an
    # ineligible spouse, whether or not aged, blind or disabled (20 CFR
    # 416.1160(d)).
    spouse_earned = msp_spouse_value(person("ssi_earned_income", year), spouse)
    spouse_unearned = msp_spouse_value(person("ssi_unearned_income", year), spouse)
    allocations = add(person.tax_unit, year, ["ssi_ineligible_child_allocation"])
    earned_left = max_(spouse_earned - max_(allocations - spouse_unearned, 0), 0)
    unearned_left = max_(spouse_unearned - allocations, 0)
    return earned_left, unearned_left
