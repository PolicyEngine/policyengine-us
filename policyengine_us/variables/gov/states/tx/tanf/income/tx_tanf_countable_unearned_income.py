from policyengine_us.model_api import *


class tx_tanf_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas TANF countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1340-income-limits"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        gross_unearned = spm_unit("tx_tanf_gross_unearned_income", period)

        # Apply child support disregard if applicable
        # For now, using gross unearned directly
        # Full implementation would include child support disregard

        return gross_unearned
