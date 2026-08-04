from policyengine_us.model_api import *


class az_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Arizona Child Care Assistance Program based on income"
    definition_period = MONTH
    defined_for = StateCode.AZ
    reference = "https://des.az.gov/sites/default/files/dl/CCA-0229AFY26.pdf#page=1"

    def formula(spm_unit, period, parameters):
        return spm_unit("az_ccap_countable_income", period) <= spm_unit(
            "az_ccap_income_limit", period
        )
