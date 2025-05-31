from policyengine_us.model_api import *


class il_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Illinois TANF eligible"
    definition_period = YEAR
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        # Illinois-specific TANF eligibility
        # This is a simplified version - should be enhanced with IL-specific rules
        
        # Basic demographic eligibility - has children
        has_child = spm_unit.sum(spm_unit.members("is_child", period)) > 0

        # Basic income test (simplified)
        household_size = spm_unit("spm_unit_size", period)
        p = parameters(period).gov.states.il.dhs.tanf.cash.amount
        # Convert to string and check if in parameter keys
        household_size_str = household_size.astype(str)
        # Only check income if household size is valid (1-18)
        income_eligible = np.zeros_like(household_size, dtype=bool)
        for size in range(1, 19):  # Parameters exist for sizes 1-18
            size_str = str(size)
            mask = household_size_str == size_str
            if mask.any() and hasattr(p, "max") and size_str in p.max:
                max_amount = p.max[size_str]
                countable_income = spm_unit("il_tanf_countable_income", period)
                income_eligible[mask] = (
                    countable_income[mask] <= max_amount * 2
                )  # Simplified test

        return has_child & income_eligible
