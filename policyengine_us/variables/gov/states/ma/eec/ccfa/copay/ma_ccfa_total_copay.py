from policyengine_us.model_api import *


class ma_ccfa_total_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Massachusetts Child Care Financial Assistance (CCFA) parent total copay"
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=76"

    def formula(spm_unit, period, parameters):
        # TAFDC recipients get free child care (no copay)
        tafdc_eligible = spm_unit("ma_tafdc_eligible", period)

        p = parameters(period).gov.states.ma.eec.ccfa.copay.ratio
        base_copay = spm_unit("ma_ccfa_base_copay", period)
        eligible_child = spm_unit.members("ma_ccfa_eligible_child", period)
        num_children = spm_unit.sum(eligible_child)

        first_child_fee = (num_children >= 1) * (base_copay * p.first_child)
        second_child_fee = (num_children >= 2) * (base_copay * p.second_child)

        additional_children_count = max_(0, num_children - 2)
        additional_children_fee = additional_children_count * (
            base_copay * p.additional_child
        )

        total_copay = (
            first_child_fee + second_child_fee + additional_children_fee
        )

        # Return zero copay for TAFDC recipients
        return where(tafdc_eligible, 0, total_copay)
