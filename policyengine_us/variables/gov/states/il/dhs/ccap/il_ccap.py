from policyengine_us.model_api import *


class il_ccap_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois Child Care Assistance Program (CCAP) benefit amount"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-50.320"
    defined_for = "il_ccap_eligible"

    def formula(spm_unit, period, parameters):
        childcare_expense = add(
            spm_unit, period, ["pre_subsidy_childcare_expenses"]
        )
        # Parents need to pay this minimum amount to day care provider
        # The CCAP will help parents pay the rest of the childcare expense
        parent_copayment = spm_unit("il_ccap_parent_copayment", period)
        subsidized_amount = max_(childcare_expense - parent_copayment, 0)
        uncapped_payment = add(spm_unit, period, ["il_ccap_payment_per_child"])
        return min_(subsidized_amount, uncapped_payment)
