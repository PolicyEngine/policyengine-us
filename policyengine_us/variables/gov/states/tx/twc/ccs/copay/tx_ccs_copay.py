from policyengine_us.model_api import *


class tx_ccs_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Texas Child Care Services (CCS) copayment"
    definition_period = MONTH
    reference = "https://wspanhandle.com/child-care/for-parents/"
    defined_for = "tx_ccs_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.twc.ccs.copay.rate

        income = spm_unit("tx_ccs_countable_income", period)
        smi = spm_unit("hhs_smi", period)
        smi_ratio = where(smi > 0, income / smi, 0)

        eligible_children = spm_unit.sum(
            spm_unit.members("tx_ccs_eligible_child", period)
        )

        # Derive linear formula constants from PSoC chart brackets.
        # First child rate is linear: base + slope * (smi_ratio - min_smi)
        fc = p.first_child
        min_smi = fc.thresholds[0]
        base_rate = fc.amounts[0]
        slope = (fc.amounts[1] - fc.amounts[0]) / (
            fc.thresholds[1] - fc.thresholds[0]
        )

        raw_first_child_rate = where(
            smi_ratio < min_smi,
            0,
            base_rate + (smi_ratio - min_smi) * slope,
        )
        max_rate = p.maximum
        first_child_rate = min_(raw_first_child_rate, max_rate)

        # Additional child rate is linear: smi_ratio * factor
        factor = p.additional_child
        additional_children = max_(eligible_children - 1, 0)
        additional_child_rate = where(
            first_child_rate >= max_rate,
            0,
            smi_ratio * factor * additional_children,
        )

        # Total rate capped at maximum, then applied to income.
        total_rate = min_(first_child_rate + additional_child_rate, max_rate)
        return total_rate * income
