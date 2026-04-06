from policyengine_us.model_api import *


class sd_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Income eligible for South Dakota TANF"
    definition_period = MONTH
    reference = "https://sdlegislature.gov/Rules/Administrative/67:10:05:03"
    defined_for = StateCode.SD

    def formula(spm_unit, period, parameters):
        countable_income = spm_unit("sd_tanf_countable_income", period)
        payment_standard = spm_unit("sd_tanf_payment_standard", period)
        return countable_income <= payment_standard
