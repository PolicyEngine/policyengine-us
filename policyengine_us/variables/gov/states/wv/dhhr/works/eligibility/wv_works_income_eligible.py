from policyengine_us.model_api import *


class wv_works_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "West Virginia WV Works income eligible"
    definition_period = MONTH
    reference = "https://bfa.wv.gov/media/2766/download?inline#page=588"
    defined_for = StateCode.WV

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wv.dhhr.works
        gross_income = add(
            spm_unit,
            period,
            ["tanf_gross_earned_income", "tanf_gross_unearned_income"],
        )
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(size, p.max_household_size)
        income_limit = p.income.standard_of_need.amount[capped_size]
        return gross_income <= income_limit
