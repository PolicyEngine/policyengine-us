from policyengine_us.model_api import *


class ca_cc_general_assistance(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Contra Costa County General Assistance"
    definition_period = MONTH
    defined_for = "ca_cc_general_assistance_eligible"
    reference = "https://ehsd.org/aging-and-adult-services/general-assistance/"

    def formula(spm_unit, period, parameters):
        maximum_grant = spm_unit("ca_cc_general_assistance_maximum_grant", period)
        countable_income = spm_unit("ca_cc_general_assistance_countable_income", period)
        # Fill-the-gap: the maximum grant minus net countable income. Floor
        # countable income at zero so net-negative flows (e.g. self-employment
        # losses) cannot inflate the grant above the maximum.
        return max_(maximum_grant - max_(countable_income, 0), 0)
