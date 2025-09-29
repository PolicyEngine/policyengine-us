from policyengine_us.model_api import *


class tx_ccs_maximum_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas Child Care Services program maximum payment"
    unit = USD
    definition_period = MONTH
    defined_for = "tx_ccs_eligible"

    def formula(spm_unit, period, parameters):
        total_reimbursement = add(spm_unit, period, ["tx_ccs_payment_rate"])
        parent_fee = spm_unit("tx_ccs_copay", period)
        return max_(total_reimbursement - parent_fee, 0)
