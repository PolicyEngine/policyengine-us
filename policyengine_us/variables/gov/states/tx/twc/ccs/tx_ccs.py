from policyengine_us.model_api import *


class tx_ccs(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Texas Child Care Services (CC) program benefit amount"
    definition_period = MONTH
    defined_for = "tx_ccs_eligible"

    def formula(spm_unit, period, parameters):
        # Per TWC CCS Provider Handbook Ch. 6 and 40 TAC §809.92, the Board's
        # maximum reimbursement rate is inclusive of the Parent Share of Cost.
        # Cap the provider charge at the max rate first, then deduct the copay.
        copay = spm_unit("tx_ccs_copay", period)
        maximum_payment = add(spm_unit, period, ["tx_ccs_payment_rate"])
        pre_subsidy_childcare_expense = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        capped_expense = min_(pre_subsidy_childcare_expense, maximum_payment)
        return max_(capped_expense - copay, 0)
