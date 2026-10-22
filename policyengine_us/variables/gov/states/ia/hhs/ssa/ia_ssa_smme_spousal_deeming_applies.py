from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ia.hhs.ssa._smme_spouse_income import (
    smme_spouse_income,
)


class ia_ssa_smme_spousal_deeming_applies(Variable):
    value_type = bool
    entity = Person
    label = "Iowa SMME deems spouse income to an applicant working above the SGA level"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1163",
        # 8-E PDF pages 11-13
        "https://hhs.iowa.gov/media/4011/download?inline#page=11",
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
        earned, unearned = smme_spouse_income(person, period)
        p = parameters(period).gov.ssa.ssi.amount
        return (
            applicant
            & person("ia_ssa_has_spouse", period)
            & (earned + unearned > p.couple - p.individual)
        )
