from policyengine_us.model_api import *


def ia_ssa_smme_spouse_is_not_ineligible(person, period):
    """Whether the other member of a two-person marital unit is not an
    ineligible spouse under 8-E p.12: a person SSI treats as aged, blind or
    disabled, or an SMME applicant working above the SGA level, who has full
    non-MAGI-related Medicaid (8-F PDF page 73, 1619(b) group). For an
    applicant whom SSI does not count, any such member is the spouse.
    Callers gate on ia_ssa_has_spouse, so the marital-unit sum less the
    person's own value is the spouse's."""
    abd = person("is_ssi_aged_blind_disabled", period.this_year)
    sga_applicant = (
        person("meets_ssi_disability_criteria", period.this_year)
        & ~abd
        & person("ia_ssa_smme_coverage_eligible", period)
    )
    status = abd | sga_applicant
    return person.marital_unit.sum(status) - status > 0


def ia_ssa_smme_spouse_is_sga_applicant(person, period):
    """Whether a person SSI treats as aged, blind or disabled is married to
    an SMME applicant working above the SGA level whose SMME income combines
    the couple's income. SSI deems from that applicant, but under 8-E p.12
    the applicant is not an ineligible spouse, so the couple is combined.
    The applicant's flag requires ia_ssa_has_spouse, so the marital-unit sum
    less the person's own value is the spouse's."""
    applicant = person("ia_ssa_smme_spousal_deeming_applies", period) & person(
        "ia_ssa_smme_coverage_eligible", period
    )
    abd = person("is_ssi_aged_blind_disabled", period.this_year)
    return abd & (person.marital_unit.sum(applicant) - applicant > 0)


def ia_ssa_smme_spouse_income(person, period):
    """A spouse's SSI earned and unearned income. For an ineligible spouse,
    allocations for ineligible children are deducted, from unearned income
    first (20 CFR 416.1163(b)(3)). A spouse who is not an ineligible spouse
    is combined as for an eligible couple, with no allocations and after the
    spouse's own student earned income exclusion (20 CFR 416.1112(c)(3)).
    Callers gate on ia_ssa_has_spouse, so the marital-unit sum less the
    person's own value is the spouse's. As in SSI's own deeming, support and
    alimony the spouse pays are not deducted (20 CFR 416.1161(a)(10), 8-E
    p.12; issue 10454), children are found through the applicant's tax unit,
    and no allocation is skipped for a child who receives public
    income-maintenance payments (416.1163(b))."""
    earned = person("ssi_earned_income", period)
    unearned = person("ssi_unearned_income", period)
    exclusion = person("ssi_blind_or_disabled_working_student_exclusion", period)
    not_ineligible = ia_ssa_smme_spouse_is_not_ineligible(person, period)
    spouse_exclusion = (person.marital_unit.sum(exclusion) - exclusion) * not_ineligible
    spouse_earned = max_(person.marital_unit.sum(earned) - earned - spouse_exclusion, 0)
    spouse_unearned = person.marital_unit.sum(unearned) - unearned
    allocations = (
        add(person.tax_unit, period, ["ssi_ineligible_child_allocation"])
        * ~not_ineligible
    )
    unearned_left = max_(spouse_unearned - allocations, 0)
    earned_left = max_(spouse_earned - max_(allocations - spouse_unearned, 0), 0)
    return earned_left, unearned_left
