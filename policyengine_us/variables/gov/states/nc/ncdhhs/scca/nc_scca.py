from policyengine_us.model_api import *


class nc_scca(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina Subsidized Child Care Assistance Program"
    unit = USD
    definition_period = MONTH
    defined_for = "nc_scca_entry_eligible"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        age_eligible = person("nc_scca_child_age_eligible", period)

        # Collect the market rates only for eligible children
        total_market_rate = spm_unit.sum(
            person("nc_scca_market_rate", period) * age_eligible
        )

        parent_fee = spm_unit("nc_scca_parent_fee", period)
        uncapped_amount = max_(total_market_rate - parent_fee, 0)
        childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        return min_(childcare_expenses, uncapped_amount)
