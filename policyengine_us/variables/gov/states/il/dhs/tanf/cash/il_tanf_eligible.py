from policyengine_us.model_api import *


class il_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Illinois TANF eligible"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        # Illinois-specific TANF eligibility
        # This is a simplified version - should be enhanced with IL-specific rules
        household = spm_unit.household
        in_il = household("state_code_str", period) == "IL"

        # Basic demographic eligibility - has children
        has_child = spm_unit.sum(spm_unit.members("is_child", period)) > 0

        # Basic income test (simplified)
        household_size = spm_unit("spm_unit_size", period).astype(str)
        p = parameters(period).gov.states.il.dhs.tanf.cash.amount
        if hasattr(p, "max") and household_size in p.max:
            max_amount = p.max[household_size]
            countable_income = spm_unit("il_tanf_countable_income", period)
            income_eligible = (
                countable_income <= max_amount * 2
            )  # Simplified test
        else:
            income_eligible = False

        return in_il & has_child & income_eligible
