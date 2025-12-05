from policyengine_us.model_api import *


class mn_mfip_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.revisor.mn.gov/statutes/cite/256P.03"
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mn.dcyf.mfip.income.earned_income_disregard
        gross_earned = spm_unit("tanf_gross_earned_income", period)
        after_flat = max_(gross_earned - p.flat_amount, 0)
        return after_flat * (1 - p.rate)
