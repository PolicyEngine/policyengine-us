from policyengine_us.model_api import *


class tx_ccs_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Texas Child Care Services (CCS) copayment"
    definition_period = MONTH
    reference = "https://wspanhandle.com/child-care/for-parents/"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.twc.ccs.copay

        # Get household income and SMI ratio
        income = spm_unit("tx_ccs_countable_income", period)
        smi = spm_unit("hhs_smi", period)
        income_to_smi_ratio = income / smi

        # Count eligible children in care
        eligible_children = spm_unit.sum(
            spm_unit.members("tx_ccs_eligible_child", period)
        )

        # Calculate copayment based on income bracket
        # Use Panhandle Region's value
        first_child_fee = p.first_child_fee.calc(income_to_smi_ratio)
        additional_child_fee = p.additional_child_fee.calc(income_to_smi_ratio)

        # Total copayment = first child + (additional children * additional child fee)
        additional_children = max_(eligible_children - 1, 0)
        total_copay = first_child_fee + (
            additional_children * additional_child_fee
        )

        return where(eligible_children > 0, total_copay, 0)
