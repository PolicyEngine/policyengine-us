from policyengine_us.model_api import *


class ca_smc_general_assistance_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for San Mateo County General Assistance due to income"
    definition_period = MONTH
    defined_for = "in_smc"
    reference = "https://www.smcgov.org/media/153295/download?inline=#page=2"

    def formula(spm_unit, period, parameters):
        income = spm_unit("ca_smc_general_assistance_countable_income", period)
        standard = spm_unit("ca_smc_general_assistance_payment_standard", period)
        return income <= standard
