from policyengine_us.model_api import *


class nj_wfnj(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Jersey WFNJ benefit"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NJ
    reference = (
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-90-3-3"
    )

    def formula(spm_unit, period, parameters):
        eligible = spm_unit("nj_wfnj_eligible", period)
        maximum_benefit = spm_unit("nj_wfnj_maximum_benefit", period)
        countable_income = add(
            spm_unit,
            period,
            [
                "nj_wfnj_countable_earned_income",
                "nj_wfnj_countable_gross_unearned_income",
            ],
        )
        # Benefit = maximum benefit - countable income
        benefit = max_(maximum_benefit - countable_income, 0)
        return where(eligible, benefit, 0)
