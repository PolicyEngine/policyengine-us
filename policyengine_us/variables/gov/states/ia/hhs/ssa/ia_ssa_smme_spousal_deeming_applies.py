from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ia.hhs.ssa._smme_spouse_income import (
    smme_spouse_income,
    smme_spouse_is_aged_blind_disabled,
)


class ia_ssa_smme_spousal_deeming_applies(Variable):
    value_type = bool
    entity = Person
    label = "Iowa SMME deems spouse income to an applicant working above the SGA level"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1163",
        "https://www.ecfr.gov/current/title-20/section-416.1167",
        # 8-E PDF pages 11-13
        "https://hhs.iowa.gov/media/4011/download?inline#page=11",
        # 8-F PDF pages 73-74
        "https://hhs.iowa.gov/media/4012/download?inline#page=73",
    )

    def formula(person, period, parameters):
        # 6-B Income (SMME) p.77 determines income "according to SSI income
        # criteria", and 8-E pp.11-13 deem an ineligible spouse's income for
        # State Supplementary Assistance groups other than the Medically
        # Needy, in-home care, dependent person and MEPD groups. SSI's deeming
        # variables apply only to people SSI treats as aged, blind or
        # disabled, so this test covers a disabled applicant working above the
        # SGA level (Iowa Code 249.3(4)(a)(2), (c)): a spouse's income after
        # child allocations is deemed when it is more than the couple rate
        # less the individual rate.
        applicant = person("meets_ssi_disability_criteria", period.this_year) & ~person(
            "is_ssi_aged_blind_disabled", period.this_year
        )
        # 8-E p.11 deems only while the applicant lives "in the same
        # household" with the spouse. Under 20 CFR 416.1167(a)(1) an absence
        # is temporary only if the person returns in the same or the next
        # month, so a spouse (or the applicant) in a medical treatment
        # facility for the month is not a household member and nothing is
        # deemed (ia_ssa.yaml Case 96).
        # NOTE: Intent to return is not modeled, as in
        # ssi_couple_computation_applies.
        apart = person.marital_unit.any(
            person("ssi_lives_in_medical_treatment_facility", period)
        )
        # 8-E p.12: "An ineligible spouse is a spouse who is not eligible for
        # SSI or non-MAGI-related Medicaid, or State Supplementary
        # Assistance." Those groups are for aged, blind or disabled people
        # (8-F PDF pages 73-74), so, as is_ssi_ineligible_spouse does, a spouse
        # SSI treats as aged, blind or disabled is not an ineligible spouse: the
        # couple's income is combined with no $497 test, as SSI and
        # msp_countable_income combine an eligible couple's income.
        # NOTE: 8-E tests eligibility for SSI, non-MAGI-related Medicaid or
        # State Supplementary Assistance. The model uses SSI's aged, blind or
        # disabled status, so an aged, blind or disabled spouse who qualifies
        # for none of them is combined rather than deemed.
        eligible_spouse = smme_spouse_is_aged_blind_disabled(person, period)
        earned, unearned = smme_spouse_income(person, period)
        p = parameters(period).gov.ssa.ssi.amount
        return (
            applicant
            & person("ia_ssa_has_spouse", period)
            & ~apart
            & (eligible_spouse | (earned + unearned > p.couple - p.individual))
        )
