from policyengine_us.model_api import *


class dc_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for DC Temporary Assistance for Needy Families (TANF) due to income"
    definition_period = MONTH
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.10"
    )
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        countable_income = spm_unit("dc_tanf_countable_income", period)
        standard_payment = spm_unit("dc_tanf_standard_payment", period)
        return countable_income <= standard_payment
