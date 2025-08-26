from policyengine_us.model_api import *


class id_liheap_heating_assistance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Idaho LIHEAP heating assistance"
    unit = USD
    definition_period = YEAR
    defined_for = "id_liheap_eligible"
    reference = "https://liheapch.acf.gov/profiles/Idaho.htm"
    documentation = "Regular heating assistance benefit amount for eligible households"

    def formula(spm_unit, period, parameters):
        # Get parameters
        p = parameters(period).gov.states.id.dhw.liheap.heating_assistance
        
        # Get household income to determine benefit level
        household_income = spm_unit("id_liheap_income", period)
        income_limit = spm_unit.members.person("id_liheap_income_limit", period).max()
        
        # Calculate income ratio (lower ratio = more need)
        income_ratio = household_income / where(income_limit > 0, income_limit, 1)
        
        # Benefit calculation based on income level
        # This is a simplified calculation - actual calculation may vary
        # Lower income gets higher benefit
        base_benefit = where(
            income_ratio <= 0.3,
            p.max,  # Very low income gets maximum
            where(
                income_ratio <= 0.6,
                p.max * 0.75,  # Moderate low income
                where(
                    income_ratio <= 0.8,
                    p.max * 0.5,  # Higher low income
                    p.min  # Near limit gets minimum
                )
            )
        )
        
        # Check for priority household status (may affect benefit level)
        is_priority = spm_unit.members("id_liheap_priority_household", period).any()
        
        # Priority households may receive higher benefits
        benefit_amount = where(
            is_priority,
            base_benefit * 1.1,  # 10% bonus for priority households
            base_benefit
        )
        
        # Cap at maximum benefit
        benefit_amount = min_(benefit_amount, p.max)
        
        # Ensure at least minimum benefit for eligible households
        benefit_amount = max_(benefit_amount, p.min)
        
        # Limit by actual heating expense
        actual_expense = add(spm_unit, period, [
            "heating_cooling_expense",
            "gas_expense",
            "electricity_expense"
        ])
        
        return min_(benefit_amount, actual_expense)