from policyengine_us.model_api import *


class mn_mfip_family_wage_level(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP Family Wage Level"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/142G.02#stat.142G.02.42"
    )
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mn.dcyf.mfip.income
        payment_standard = spm_unit("mn_mfip_payment_standard", period)
        return payment_standard * p.family_wage_level_multiplier
