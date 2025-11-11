from policyengine_us.model_api import *


class wa_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Washington TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = ("https://app.leg.wa.gov/wac/default.aspx?cite=388-450-0170",)
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        # Get parameters
        p = parameters(period).gov.states.wa.dshs.tanf.income

        # Get gross earned income
        gross_earned = spm_unit("wa_tanf_gross_earned_income", period)

        # Apply family earnings disregard ($500)
        income_after_disregard = max_(
            gross_earned - p.earned_income_disregard, 0
        )

        # Apply 50% work incentive (count 50% of remaining income)
        countable = income_after_disregard * p.work_incentive_percentage

        return countable
