from policyengine_us.model_api import *


class mn_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.revisor.mn.gov/statutes/cite/256P.03"
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        gross_earned = spm_unit("tanf_gross_earned_income", period)
        p = parameters(
            period
        ).gov.states.mn.dhs.tanf.income.earned_income_disregard

        flat_disregard = p.flat_amount
        remaining = max_(gross_earned - flat_disregard, 0)
        percentage_disregard = remaining * p.rate

        total_disregard = flat_disregard + percentage_disregard
        return max_(gross_earned - total_disregard, 0)
