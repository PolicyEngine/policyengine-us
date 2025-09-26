from policyengine_us.model_api import *


class tx_tanf_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas TANF gross earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1320-types-income"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        earned_income_sources = [
            "employment_income",
            "self_employment_income",
        ]

        total_earned = add(spm_unit, period, earned_income_sources)

        # Convert to monthly if needed
        # Using 4.33 for weekly, 2.17 for bi-weekly per A-1350
        return total_earned
