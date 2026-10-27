from policyengine_us.model_api import *


class az_liheap_categorically_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Arizona LIHEAP categorically eligible"
    documentation = "A household member receives DES Cash Assistance (TANF) or Nutrition Assistance (SNAP), which satisfies the income requirement; all other eligibility criteria still apply."
    reference = (
        # PDF pages 3-4, 7
        "https://des.az.gov/sites/default/files/dl/CCSD-LIHEAP-Policy.pdf#page=3",
        "https://liheapch.acf.gov/docs/2026/state-plans/AZ_Plan_2026.pdf#page=5",
    )
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.az.des.liheap.eligibility
        # Section VI.A.6.b.i: "If one (1) Household member's current enrollment
        # in Cash Assistance or Nutrition Assistance is verified, the Household
        # will be considered categorically eligible." A positive modeled
        # benefit in the year stands for current enrollment; add() sums the
        # MONTH-defined snap over the year, and the annual tanf includes
        # Arizona Cash Assistance. Both are take-up gated. SSI and veterans
        # programs do not confer categorical eligibility (plan Section 1.4).
        return add(spm_unit, period, p.categorical_programs) > 0
