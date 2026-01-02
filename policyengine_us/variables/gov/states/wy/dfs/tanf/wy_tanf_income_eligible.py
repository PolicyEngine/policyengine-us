from policyengine_us.model_api import *


class wy_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Wyoming TANF income eligible"
    definition_period = MONTH
    reference = (
        "https://dfs.wyo.gov/about/policy-manuals/snap-and-power-policy-manual/table-ii-power-income-limits/",
        "https://dfs.wyo.gov/accordions/snap-and-power-policy-manual-1100-extended-menu/",
    )
    defined_for = StateCode.WY

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wy.dfs.tanf
        countable_income = spm_unit("wy_tanf_countable_income", period)
        unit_size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(unit_size, p.max_unit_size)
        income_limit = p.eligibility.income.limit[capped_size]
        return countable_income < income_limit
