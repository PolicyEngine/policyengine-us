from policyengine_us.model_api import *


class mn_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP countable income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.revisor.mn.gov/statutes/cite/142G/pdf"
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        return add(
            spm_unit,
            period,
            [
                "mn_tanf_countable_earned_income",
                "mn_tanf_countable_unearned_income",
            ],
        )
