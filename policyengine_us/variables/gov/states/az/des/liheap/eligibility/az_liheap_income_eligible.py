from policyengine_us.model_api import *


class az_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Arizona LIHEAP income eligible"
    documentation = "Countable household income does not exceed the Appendix A income limit for the eligible household size."
    reference = (
        # PDF pages 8, 39
        "https://des.az.gov/sites/default/files/dl/CCSD-LIHEAP-Policy.pdf#page=8",
        "https://liheapch.acf.gov/docs/2026/state-plans/AZ_Plan_2026.pdf#page=9",
    )
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        income = spm_unit("az_liheap_countable_income", period)
        limit = spm_unit("az_liheap_income_limit", period)
        # Section VI.A.6.c.i: income "must be at or below" the limit, so a
        # household exactly at the limit qualifies.
        return income <= limit
