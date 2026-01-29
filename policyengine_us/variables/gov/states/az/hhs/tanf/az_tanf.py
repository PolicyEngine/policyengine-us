from policyengine_us.model_api import *


class az_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona TANF"
    unit = USD
    definition_period = MONTH
    reference = "https://www.azleg.gov/ars/46/00207-01.htm"
    defined_for = "az_tanf_eligible"

    def formula(spm_unit, period, parameters):
        payment_standard = spm_unit("az_tanf_payment_standard", period)
        countable_income = spm_unit("az_tanf_countable_income", period)
        return max_(payment_standard - countable_income, 0)
