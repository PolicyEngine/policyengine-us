from policyengine_us.model_api import *


class tx_ccs(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Texas Child Care Services (CC) program benefit amount"
    definition_period = MONTH
    defined_for = "tx_ccs_eligible"

    def formula(spm_unit, period, parameters):
        copay = spm_unit("tx_ccs_copay", period)
        maximum_payment = add(spm_unit, period, ["tx_ccs_payment_rate"])
        pre_subsidy_childcare_expense = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        uncapped_subsidy_amount = max_(
            pre_subsidy_childcare_expense - copay, 0
        )
        return min_(uncapped_subsidy_amount, maximum_payment)
