from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ia.hhs.ssa._ia_ssa_smme_spouse_income import (
    ia_ssa_smme_spouse_income,
    ia_ssa_smme_spouse_is_not_ineligible,
)


class ia_ssa_smme_spousal_deeming_applies(Variable):
    value_type = bool
    entity = Person
    label = "Iowa SMME counts a spouse's income for an applicant working above the SGA level"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = (
        # Iowa Code 249.3(4)(a)(2) and (c)
        "https://www.legis.iowa.gov/docs/code/249.pdf#page=2",
        "https://www.law.cornell.edu/cfr/text/20/416.1163",
        "https://www.ecfr.gov/current/title-20/section-416.1167",
        # 8-E PDF pages 11-13
        "https://hhs.iowa.gov/media/4011/download?inline#page=11",
        # 8-F PDF pages 73-74, 88, 114
        "https://hhs.iowa.gov/media/4012/download?inline#page=73",
        # 6-B PDF page 76
        "https://hhs.iowa.gov/media/3987/download?inline=#page=76",
    )

    def formula(person, period, parameters):
        # 6-B Income (SMME) p.77 determines income "according to SSI income
        # criteria", and 8-E p.11 determines deemed income "for
        # non-MAGI-related Medicaid and State Supplementary Assistance
        # coverage groups according to SSI policies", except the Medically
        # Needy, in-home health-related care, dependent person and MEPD
        # groups. SSI's deeming variables apply only to people SSI treats as
        # aged, blind or disabled, so this test covers a disabled applicant
        # working above the SGA level (Iowa Code 249.3(4)(a)(2), (c)): it is
        # true when the spouse is not an ineligible spouse (income combined)
        # or the spouse's income after child allocations is more than the
        # couple rate less the individual rate (income deemed), unless either
        # spouse is in a medical facility.
        applicant = person("meets_ssi_disability_criteria", period.this_year) & ~person(
            "is_ssi_aged_blind_disabled", period.this_year
        )
        # 8-E p.11 deems only while the applicant lives "in the same
        # household" with the spouse. Under 20 CFR 416.1167(a)(1) an absence
        # is temporary only if the person returns in the same or the next
        # month, so a spouse (or the applicant) in a medical treatment
        # facility for the month is not a household member and nothing is
        # deemed, whoever pays for the stay (ia_ssa.yaml Cases 96 and 99).
        # NOTE: Intent to return is not modeled, as in
        # ssi_couple_computation_applies. The facility input is read as
        # residence for the whole month (20 CFR 416.414(a)(1)); 8-E p.11 deems
        # for a month in which the applicant lived "for any part of a month in
        # the same household" with the spouse. A spouse in a residential care
        # facility after the month of entry, whom ia_ssa_care_countable_income
        # budgets alone, is still treated as a household member here.
        apart = person.marital_unit.any(
            person("ssi_lives_in_medical_treatment_facility", period)
        )
        # 8-E p.12: "An ineligible spouse is a spouse who is not eligible for
        # SSI or non-MAGI-related Medicaid, or State Supplementary Assistance."
        # Those groups are for aged, blind or disabled people (8-F PDF pages
        # 73-74). SMME is itself State Supplementary Assistance, and an SMME
        # applicant must receive full Medicaid under "a Medicaid coverage group
        # that does not rely on eligibility for SSA" (6-B PDF page 76), which
        # ia_ssa_smme_coverage_eligible records. For a disabled worker above
        # the SGA level that can be MEPD with no premium, where SGA "is not
        # considered" (8-F PDF page 114), or the 1619(b) group of former SSI
        # recipients (8-F PDF page 88). So a spouse SSI treats as aged, blind
        # or disabled, or an SMME applicant working above the SGA level, is not
        # an ineligible spouse: the couple's income is combined with no $497
        # test, as SSI and msp_countable_income combine an eligible couple's
        # income (ia_ssa.yaml Cases 97, 102, 103 and 107). This test is broader
        # than is_ssi_ineligible_spouse.
        # NOTE: 8-E tests eligibility for SSI, non-MAGI-related Medicaid or
        # State Supplementary Assistance. The model uses SSI's aged, blind or
        # disabled status and the SMME coverage input, so an aged, blind or
        # disabled spouse who qualifies for none of them is combined rather
        # than deemed, and a disabled spouse working above the SGA level who
        # has another non-MAGI-related Medicaid group, such as MEPD, but no
        # SMME coverage is deemed rather than combined.
        not_ineligible = ia_ssa_smme_spouse_is_not_ineligible(person, period)
        earned, unearned = ia_ssa_smme_spouse_income(person, period)
        p = parameters(period).gov.ssa.ssi.amount
        return (
            applicant
            & person("ia_ssa_has_spouse", period)
            & ~apart
            & (not_ineligible | (earned + unearned > p.couple - p.individual))
        )
