from policyengine_us.model_api import *


class dc_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC Temporary Assistance for Needy Families (TANF)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.52"
    )
    defined_for = "dc_tanf_eligible"

    def formula(spm_unit, period, parameters):
        standard_payment = spm_unit("dc_tanf_standard_payment", period)
        countable_income = spm_unit("dc_tanf_countable_income", period)
        return max_(standard_payment - countable_income, 0)
