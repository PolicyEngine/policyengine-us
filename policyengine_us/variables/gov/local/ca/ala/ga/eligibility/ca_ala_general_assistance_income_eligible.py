from policyengine_us.model_api import *


class ala_general_assistance_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Alameda County General Assistance based on income requirements"
    definition_period = MONTH
    defined_for = "in_ala"
    reference = "https://www.alamedacountysocialservices.org/our-services/Work-and-Money/General-Assistance/index"

    def formula(spm_unit, period, parameters):
        income = spm_unit("ala_general_assistance_countable_income", period)
        limit = spm_unit("ala_general_assistance_base_amount", period)
        return income < limit
