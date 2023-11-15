from policyengine_us.model_api import *


class ca_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Cash Benefit"
    unit = USD
    definition_period = YEAR
    defined_for = "ca_tanf_eligible"

    def formula(spm_unit, period, parameters):
        maximum_payment = spm_unit("ca_tanf_maximum_payment", period)
        countable_income = spm_unit(
            "ca_tanf_countable_income_recipient", period
        )
        return max_(maximum_payment - countable_income, 0)
