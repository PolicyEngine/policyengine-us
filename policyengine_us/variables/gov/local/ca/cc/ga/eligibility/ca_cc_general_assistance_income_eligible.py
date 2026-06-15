from policyengine_us.model_api import *


class ca_cc_general_assistance_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Contra Costa County General Assistance based on income requirements"
    definition_period = MONTH
    defined_for = "in_cc"
    reference = "https://ehsd.org/aging-and-adult-services/general-assistance/"

    def formula(spm_unit, period, parameters):
        income = spm_unit("ca_cc_general_assistance_countable_income", period)
        maximum_grant = spm_unit("ca_cc_general_assistance_maximum_grant", period)
        # Countable income must be strictly below the grant standard ("earnings
        # less than the maximum allowable grant").
        return income < maximum_grant
