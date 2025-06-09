from policyengine_us.model_api import *


class dc_gac(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC General Assistance for Children (GAC)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.05a"
    )
    defined_for = "dc_gac_eligible"

    def formula(spm_unit, period, parameters):
        countable_income = spm_unit("dc_gac_countable_income", period)
        standard_payment = spm_unit("dc_gac_standard_payment", period)
        return max_(standard_payment - countable_income, 0)
