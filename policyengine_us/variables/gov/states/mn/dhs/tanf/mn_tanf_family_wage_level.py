from policyengine_us.model_api import *


class mn_tanf_family_wage_level(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP Family Wage Level"
    unit = USD
    definition_period = MONTH
    reference = "https://www.revisor.mn.gov/statutes/cite/142G/pdf"
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        payment_standard = spm_unit("mn_tanf_payment_standard", period)
        multiplier = parameters(
            period
        ).gov.states.mn.dhs.tanf.income.family_wage_level_multiplier
        return payment_standard * multiplier
