from policyengine_us.model_api import *


class nv_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nevada Temporary Assistance for Needy Families (TANF)"
    unit = USD
    definition_period = MONTH
    reference = "https://dss.nv.gov/TANF/Financial_Help/"
    defined_for = "nv_tanf_eligible"

    def formula(spm_unit, period, parameters):
        payment_standard = spm_unit("nv_tanf_payment_standard", period)
        countable_income = spm_unit("nv_tanf_countable_income", period)
        # Benefit is payment standard minus countable income
        return max_(payment_standard - countable_income, 0)
