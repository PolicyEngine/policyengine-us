from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
)
from policyengine_us.variables.gov.states.ia.hhs.ssa._ia_ssa_smme_spouse_income import (
    ia_ssa_smme_spouse_income,
    ia_ssa_smme_spouse_is_sga_applicant,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class ia_ssa_smme_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Iowa SMME countable income for Medicaid coverage group"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.IA
    documentation = "SSI countable income plus any SSI payment, combined for a couple whose SSI couple computation applies. For a disabled person working above the SGA level, whom SSI does not count, the person's own income, including in-kind support and maintenance and any spouse income deemed, or combined for a spouse who is not an ineligible spouse, under SSI's rules, after SSI's exclusions, including the student earned income exclusion; or, for the aged, blind or disabled spouse of such an applicant, the couple's combined income. Deductions and financial groups of a Medicaid coverage category that differ from SSI are not modeled."
    reference = (
        # Iowa Code 249.3(4)(a)(2) and (g); PDF pages 2-3
        "https://www.legis.iowa.gov/docs/code/249.pdf#page=2",
        # 441 IAC 51.7(6)
        "https://www.legis.iowa.gov/docs/iac/chapter/441.51.pdf#page=2",
        # 6-B Income (SMME)
        "https://hhs.iowa.gov/media/3987/download?inline=#page=77",
        # 8-E Deeming from an Ineligible Spouse; PDF pages 12-13
        "https://hhs.iowa.gov/media/4011/download?inline#page=12",
    )

    def formula(person, period, parameters):
        # 6-B Income (SMME): income "is determined according to SSI income
        # criteria". ia_ssa compares it with 120 percent of the poverty
        # guideline as Iowa Code 249.3(4)(g) sets it ("at least"; see the NOTE
        # in ia_ssa). An eligible couple's combined income is compared with the
        # two-person guideline (ia_ssa.yaml Cases 47-49). With an ineligible
        # spouse, SSI countable income includes the income SSI deems from that
        # spouse, and ia_ssa then uses the two-person guideline; when SSI deems
        # nothing, 8-E p.12 says to "Process as a one-person household"
        # (Cases 83-84).
        # NOTE: Group-specific Medicaid budgeting is not modeled.
        income = person("ssi_countable_income", period) + person("ssi", period)
        # SSI counts income only for people it treats as aged, blind or
        # disabled, so ssi_countable_income is 0 for a disabled person working
        # above the SGA level, whom SMME still covers (Iowa Code
        # 249.3(4)(a)(2)). That person's own income gets SSI's income rules
        # instead: the student earned income exclusion (20 CFR
        # 416.1112(c)(3)), in-kind support and maintenance (416.1130, 416.1140)
        # and the general and earned income exclusions (ia_ssa.yaml Cases 77,
        # 87 and 88). As 8-E pp.12-13 do, a spouse's income above the couple
        # rate less the individual rate, or the income of a spouse who is not
        # an ineligible spouse, after that spouse's own student earned income
        # exclusion, is added before the exclusions
        # (ia_ssa_smme_spousal_deeming_applies), and ia_ssa then uses the
        # two-person guideline (for example Cases 82, 97, 102 and 103; Cases
        # 92, 96 and 99 use the one-person guideline).
        # NOTE: Income deemed from a parent is not modeled on this path. The
        # student earned income exclusion, for the applicant and for a spouse
        # who is not an ineligible spouse, follows 20 CFR 416.1112(c)(3) and
        # 42 U.S.C. 1382a(b)(1) as amended in 2004, which have no marital or
        # head-of-household test; 8-E p.19 still lists "Not married" and "Not
        # the head of the household" (Cases 87 and 106). In-kind support and
        # maintenance is the applicant's own, at the individual presumed
        # maximum value (416.1140), the individual figure 8-E gives (8-E p.56); when the
        # couple is combined, the spouse's in-kind support and maintenance and
        # the couple's presumed maximum value are not modeled.
        earned = max_(
            person("ssi_earned_income", period)
            - person("ssi_blind_or_disabled_working_student_exclusion", period),
            0,
        )
        unearned = person("ssi_unearned_income", period) + person(
            "ssi_in_kind_support_and_maintenance", period
        )
        deemed = person("ia_ssa_smme_spousal_deeming_applies", period)
        spouse_earned, spouse_unearned = ia_ssa_smme_spouse_income(person, period)
        earned = earned + deemed * spouse_earned
        unearned = unearned + deemed * spouse_unearned
        # NOTE: The aged, blind or disabled spouse's SSI payment is not added.
        # SSI does not count its own payment as income, and that payment
        # exists only because SSI treats the applicant as an ineligible spouse
        # and takes child allocations (20 CFR 416.1160(d), 416.1163(b)); the
        # eligible-couple budget (8-E p.12) gives no such payment (Case 104).
        # A spouse whom SSI pays gets no SMME (Iowa Code 249.3(4)(c); ia_ssa,
        # Case 110).
        own_income = (
            _apply_ssi_exclusions(
                earned * MONTHS_IN_YEAR, unearned * MONTHS_IN_YEAR, parameters, period
            )
            / MONTHS_IN_YEAR
        )
        counted_by_ssi = person("is_ssi_aged_blind_disabled", period.this_year)
        income = where(counted_by_ssi, income, own_income)
        # The aged, blind or disabled spouse of that applicant gets the same
        # combined income, not SSI's deeming from the applicant (Cases 98 and
        # 102).
        applicant = deemed & person("ia_ssa_smme_coverage_eligible", period)
        combined = _ssi_couple_total(
            person, period.this_year, where(applicant, income, 0)
        )
        income = where(
            ia_ssa_smme_spouse_is_sga_applicant(person, period), combined, income
        )
        # NOTE: For an eligible couple, ssi_countable_income takes off only
        # half of a student spouse's earned income exclusion (issue 10456).
        joint = person("ssi_couple_computation_applies", period)
        return where(joint, _ssi_couple_total(person, period.this_year, income), income)
