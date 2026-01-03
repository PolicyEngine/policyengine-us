from policyengine_us.model_api import *


class sd_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Dakota Temporary Assistance for Needy Families (TANF)"
    unit = USD
    definition_period = MONTH
    reference = "https://sdlegislature.gov/Rules/Administrative/67:10:05:02"
    defined_for = "sd_tanf_eligible"

    def formula(spm_unit, period, parameters):
        payment_standard = spm_unit("sd_tanf_payment_standard", period)
        countable_income = spm_unit("sd_tanf_countable_income", period)
        return max_(payment_standard - countable_income, 0)
