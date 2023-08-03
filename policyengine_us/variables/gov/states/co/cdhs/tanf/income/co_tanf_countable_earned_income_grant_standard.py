from policyengine_us.model_api import *


class co_tanf_countable_earned_income_grant_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Colorado TANF total countable earned income for grant standard"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(spm_unit, period, parameters):
        gross_earnings = spm_unit(
            "co_tanf_countable_gross_earned_income", period
        )
        p = parameters(period).gov.states.co.cdhs.tanf.income.earned_exclusion
        # Grant standard applies a percent exclusion.
        return gross_earnings * (1 - p.percent)
