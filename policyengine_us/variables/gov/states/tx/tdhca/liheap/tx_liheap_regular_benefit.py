from policyengine_us.model_api import *


class tx_liheap_regular_benefit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Texas LIHEAP regular benefit"
    unit = USD
    documentation = (
        "Regular LIHEAP benefit amount including priority adjustments"
    )
    reference = "https://www.tdhca.texas.gov/sites/default/files/2023-10/FY2024-LIHEAP-State-Plan.pdf"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.tdhca.liheap

        # Check eligibility
        eligible = spm_unit("tx_liheap_eligible", period)

        # Get base benefit
        base_benefit = spm_unit("tx_liheap_base_benefit", period)

        # Check priority group status
        is_priority = spm_unit("tx_liheap_priority_group", period)

        # Apply priority multiplier if applicable
        adjusted_benefit = where(
            is_priority,
            base_benefit * p.priority_benefit_multiplier,
            base_benefit,
        )

        # Apply minimum and maximum limits
        final_benefit = clip(
            adjusted_benefit, p.minimum_benefit, p.maximum_benefit
        )

        # Return benefit only if eligible
        return where(eligible, final_benefit, 0)
