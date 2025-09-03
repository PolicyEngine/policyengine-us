from policyengine_us.model_api import *


class nc_scca(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina Subsidized Child Care Assistance Program"
    unit = USD
    definition_period = MONTH
    defined_for = "nc_scca_entry_eligible"

    def formula(spm_unit, period, parameters):
        parent_fee = spm_unit("nc_scca_parent_fee", period)
        childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        uncapped_amount = max_(childcare_expenses - parent_fee, 0)
        maximum_payment = spm_unit("nc_scca_maximum_payment", period)
        return min_(uncapped_amount, maximum_payment)
