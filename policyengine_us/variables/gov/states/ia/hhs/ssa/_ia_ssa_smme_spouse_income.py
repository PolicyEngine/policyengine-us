from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ia.hhs.ssa._ia_ssa_spouses import (
    ia_ssa_spouse_value,
)


def ia_ssa_smme_spouse_is_not_ineligible(person, period):
    """Whether the co-resident spouse is not an
    ineligible spouse under 8-E p.12: a person SSI treats as aged, blind or
    disabled, or an SMME applicant working above the SGA level, who receives
    full Medicaid under a group that does not rely on State Supplementary
    Assistance (6-B PDF page 76), such as MEPD (8-F PDF page 114) or 1619(b)
    (8-F PDF page 88). For an
    applicant whom SSI does not count, that person's spouse is still found
    by marriage rather than SSI eligibility or tax-unit role."""
    abd = person("is_ssi_aged_blind_disabled", period.this_year)
    sga_applicant = (
        person("meets_ssi_disability_criteria", period.this_year)
        & ~abd
        & person("ia_ssa_smme_coverage_eligible", period)
    )
    status = abd | sga_applicant
    return ia_ssa_spouse_value(person, period, status)


def ia_ssa_smme_spouse_is_sga_applicant(person, period):
    """Whether a person SSI treats as aged, blind or disabled is married to
    an SMME applicant working above the SGA level whose SMME income combines
    the couple's income. SSI deems from that applicant, but under 8-E p.12
    the applicant is not an ineligible spouse, so the couple is combined.
    Unrelated household adults never enter this spouse test."""
    applicant = person("ia_ssa_smme_spousal_deeming_applies", period) & person(
        "ia_ssa_smme_coverage_eligible", period
    )
    abd = person("is_ssi_aged_blind_disabled", period.this_year)
    return abd & ia_ssa_spouse_value(person, period, applicant)


def ia_ssa_smme_spouse_income(person, period):
    """A spouse's SSI earned and unearned income. For an ineligible spouse,
    allocations for ineligible children are deducted, from unearned income
    first (20 CFR 416.1163(b)(3)). A spouse who is not an ineligible spouse
    is combined as for an eligible couple, with no allocations and after the
    spouse's own student earned income exclusion (20 CFR 416.1112(c)(3)).
    Only the identified co-resident spouse contributes. As in SSI's own deeming, support and
    alimony the spouse pays are not deducted (20 CFR 416.1161(a)(10), 8-E
    p.12; issue 10454), children are found through the applicant's tax unit,
    no allocation is skipped for a child who receives public
    income-maintenance payments (416.1163(b); both in PR 10146), and an
    ineligible spouse's student earned income is not excluded
    (416.1161(a)(27); issue 10521)."""
    earned = person("ssi_earned_income", period)
    unearned = person("ssi_unearned_income", period)
    exclusion = person("ssi_blind_or_disabled_working_student_exclusion", period)
    not_ineligible = ia_ssa_smme_spouse_is_not_ineligible(person, period)
    spouse_exclusion = ia_ssa_spouse_value(person, period, exclusion) * not_ineligible
    spouse_earned = max_(
        ia_ssa_spouse_value(person, period, earned) - spouse_exclusion, 0
    )
    spouse_unearned = ia_ssa_spouse_value(person, period, unearned)
    allocations = (
        add(person.tax_unit, period, ["ssi_ineligible_child_allocation"])
        * ~not_ineligible
    )
    unearned_left = max_(spouse_unearned - allocations, 0)
    earned_left = max_(spouse_earned - max_(allocations - spouse_unearned, 0), 0)
    return earned_left, unearned_left
