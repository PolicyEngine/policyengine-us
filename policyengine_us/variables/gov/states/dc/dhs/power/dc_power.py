from policyengine_us.model_api import *


class dc_power(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC Program on Work, Employment, and Responsibility (POWER)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.52"
    )
    defined_for = "dc_power_eligible"

    def formula(spm_unit, period, parameters):
        standard_payment = spm_unit("dc_tanf_standard_payment", period)
        countable_income = spm_unit("dc_tanf_countable_income", period)
        return max_(standard_payment - countable_income, 0)
