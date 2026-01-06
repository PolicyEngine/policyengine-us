from policyengine_us.model_api import *


class sc_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina TANF countable resources"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.SC

    def formula(spm_unit, period, parameters):
        # Resources are stocks, use period.this_year to avoid /12 conversion
        cash_assets = spm_unit("spm_unit_cash_assets", period.this_year)
        retirement = add(
            spm_unit, period.this_year, ["retirement_distributions"]
        )
        return cash_assets + retirement
