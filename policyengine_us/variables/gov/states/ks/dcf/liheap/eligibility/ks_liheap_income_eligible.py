from policyengine_us.model_api import *


class ks_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Kansas LIEAP income eligible"
    documentation = "Combined gross income of all household members does not exceed 150% of the federal poverty guideline for the countable household size, or the household is categorically income eligible."
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/KS_Plan_2026.pdf#page=8",
        "https://content.dcf.ks.gov/ees/keesm/current/keesm13000.htm",
        "https://content.dcf.ks.gov/ees/keesm/current/keesm13300.htm",
    )
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ks.dcf.liheap.eligibility
        income = spm_unit("ks_liheap_countable_income", period)
        fpg = spm_unit("ks_liheap_fpg", period)
        categorically_eligible = spm_unit(
            "ks_liheap_categorically_income_eligible", period
        )
        return categorically_eligible | (income <= fpg * p.fpg_limit)
