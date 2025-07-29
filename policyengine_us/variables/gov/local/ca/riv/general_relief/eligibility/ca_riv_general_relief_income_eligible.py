from policyengine_us.model_api import *


class ca_riv_general_relief_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Riverside County General Relief due to income"
    definition_period = MONTH
    defined_for = "in_riv"

    def formula(spm_unit, period, parameters):
        countable_income = spm_unit(
            "ca_riv_general_relief_countable_income", period
        )
        needs_standards = spm_unit(
            "ca_riv_general_relief_needs_standards", period
        )
        return countable_income <= needs_standards
