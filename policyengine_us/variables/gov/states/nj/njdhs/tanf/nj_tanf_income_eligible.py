from policyengine_us.model_api import *


class nj_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New Jersey TANF income eligible"
    definition_period = YEAR
    defined_for = StateCode.NJ

    def formula(spm_unit, period, parameters):
        income = add(
            spm_unit,
            period,
            [
                "nj_tanf_countable_earned_income",
                "nj_tanf_countable_gross_unearned_income",
            ],
        )
        maximum_allowable_income = spm_unit(
            "nj_tanf_maximum_allowable_income", period
        )
        maximum_benefit = spm_unit("nj_tanf_maximum_benefit", period)
        # New Jersey Administrative Code 10:90-3.1
        return (income <= maximum_allowable_income) & (
            income < maximum_benefit
        )
