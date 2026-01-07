from policyengine_us.model_api import *


class nj_wfnj_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New Jersey WFNJ income eligible"
    definition_period = MONTH
    defined_for = StateCode.NJ
    reference = (
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-90-3-1"
    )

    def formula(spm_unit, period, parameters):
        income = add(
            spm_unit,
            period,
            [
                "nj_wfnj_countable_earned_income",
                "nj_wfnj_countable_gross_unearned_income",
            ],
        )
        maximum_allowable_income = spm_unit(
            "nj_wfnj_maximum_allowable_income", period
        )
        maximum_benefit = spm_unit("nj_wfnj_maximum_benefit", period)
        return (income <= maximum_allowable_income) & (
            income < maximum_benefit
        )
