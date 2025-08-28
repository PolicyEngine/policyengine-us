from policyengine_us.model_api import *


class tx_liheap_high_energy_burden(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Texas LIHEAP household has high energy burden"
    documentation = """
    Determines if household's energy costs exceed 10% of income (high energy burden).
    
    Energy Burden Definition:
    Energy Burden = Annual Utility Expenses ÷ Annual Household Income
    
    High Energy Burden Threshold:
    - Texas defines high burden as ≥10% of household income spent on utilities
    - National average is approximately 3% for all households
    - Low-income households typically face 8-10% burden
    - Qualifies household for priority group status
    
    Calculation Formula:
    Energy Burden = Utility Expense / Household Income
    High Burden = Energy Burden ≥ 0.10 (10%)
    
    Example 1 - High Burden, Low Income:
    - Annual household income: $15,000
    - Annual utility expenses: $2,400 ($200/month)
    - Energy burden: $2,400 / $15,000 = 0.16 (16%)
    - Test: 16% ≥ 10% = TRUE
    - Result: HIGH ENERGY BURDEN (priority group)
    
    Example 2 - Moderate Burden, Middle Income:
    - Annual household income: $40,000
    - Annual utility expenses: $3,600 ($300/month)
    - Energy burden: $3,600 / $40,000 = 0.09 (9%)
    - Test: 9% < 10% = FALSE
    - Result: NOT HIGH BURDEN
    
    Example 3 - High Burden, Fixed Income:
    - Social Security income: $1,200/month ($14,400/year)
    - Utility expenses: $175/month ($2,100/year)
    - Energy burden: $2,100 / $14,400 = 0.146 (14.6%)
    - Test: 14.6% ≥ 10% = TRUE
    - Result: HIGH ENERGY BURDEN (priority group)
    
    Example 4 - Zero Income Edge Case:
    - Household income: $0 (temporarily unemployed)
    - Utility expenses: $150/month
    - Energy burden: Undefined (division by zero protection)
    - Result: NOT HIGH BURDEN (defaults to false for zero income)
    
    Example 5 - Just Below Threshold:
    - Annual income: $25,000
    - Annual utilities: $2,490
    - Energy burden: $2,490 / $25,000 = 0.0996 (9.96%)
    - Test: 9.96% < 10% = FALSE
    - Result: NOT HIGH BURDEN (must meet or exceed 10%)
    
    Policy Rationale:
    - High energy burden threatens household stability
    - Can force choices between heating/cooling and other necessities
    - Priority assistance helps most vulnerable households
    - Prevents utility shutoffs and health emergencies
    
    Edge Cases:
    - Zero income households: Returns false (avoids division by zero)
    - Exactly 10% burden: Qualifies as high burden (≥ not >)
    - Seasonal variations: Uses annual averages
    
    Related variables:
    - household_income: Total annual household income
    - utility_expense: Total annual utility costs
    - tx_liheap_priority_group: Uses this for priority determination
    """
    reference = [
        "https://www.tdhca.texas.gov/sites/default/files/2023-10/FY2024-LIHEAP-State-Plan.pdf",
        "42 U.S.C. 8622(2)(C) - Energy burden of low-income households",
        "DOE Low-Income Energy Affordability Data (LEAD) Tool"
    ]
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.tdhca.liheap

        # Get household income and utility expenses per State Plan Section 3.4.4
        income = spm_unit("household_income", period)
        utility_expense = spm_unit("utility_expense", period)

        # Calculate energy burden ratio per 42 U.S.C. 8622(2)(C)
        # Use where to avoid division by zero for households with no income
        energy_burden = where(income > 0, utility_expense / income, 0)

        # Check if energy burden exceeds threshold (10% in Texas)
        # Per State Plan: "Households spending 10% or more of income on energy"
        return energy_burden >= p.high_energy_burden_threshold
