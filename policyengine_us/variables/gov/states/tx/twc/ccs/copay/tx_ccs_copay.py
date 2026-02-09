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
        smi_ratio = income / smi

        eligible_children = spm_unit.sum(
            spm_unit.members("tx_ccs_eligible_child", period)
        )

        # First child rate per official TWC PSoC Calculator:
        # IF(SMI% < min_smi, 0, ((SMI% * 100 - 1) * slope) + base_rate)
        # Capped at maximum rate.
        raw_first_child_rate = where(
            smi_ratio < p.minimum_smi,
            0,
            ((smi_ratio * 100 - 1) * p.slope) + p.base_rate,
        )
        max_rate = p.maximum
        first_child_rate = min_(raw_first_child_rate, max_rate)

        # Additional child rate per official TWC PSoC Calculator:
        # IF(first_child_rate == max, 0, SMI% * factor * num_additional)
        additional_children = max_(eligible_children - 1, 0)
        additional_child_rate = where(
            first_child_rate >= max_rate,
            0,
            smi_ratio * p.additional_child_factor * additional_children,
        )

        # Total rate capped at maximum, then applied to income.
        total_rate = min_(first_child_rate + additional_child_rate, max_rate)
        return total_rate * income
