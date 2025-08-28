from policyengine_us.model_api import *


class tx_liheap_regular_benefit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Texas LIHEAP regular benefit"
    unit = USD
    documentation = """
    Calculates final regular LIHEAP benefit with priority adjustments and limits.
    
    Benefit Calculation Steps:
    1. Start with base benefit (based on household size)
    2. Apply 20% priority multiplier if household qualifies
    3. Apply minimum benefit floor ($1)
    4. Apply maximum benefit cap ($12,300)
    
    Priority Groups (receive 20% increase):
    - Households with elderly members (60+)
    - Households with disabled members
    - Households with children under 6
    - Households with high energy burden (>10% of income)
    
    Example 1 - Non-Priority Single Person:
    - Household size: 1
    - Base benefit: $6,396 (52% of $12,300)
    - Priority status: No
    - Adjusted benefit: $6,396 × 1.0 = $6,396
    - Final benefit: $6,396 (within limits)
    
    Example 2 - Priority Family with Young Child:
    - Household size: 3 (parents + 4-year-old)
    - Base benefit: $10,332 (84% of $12,300)
    - Priority status: Yes (child under 6)
    - Adjusted benefit: $10,332 × 1.2 = $12,398.40
    - Final benefit: $12,300 (capped at maximum)
    
    Example 3 - Priority Elderly Couple:
    - Household size: 2 (both over 60)
    - Base benefit: $8,364 (68% of $12,300)
    - Priority status: Yes (elderly members)
    - Adjusted benefit: $8,364 × 1.2 = $10,036.80
    - Final benefit: $10,036.80 (within limits)
    
    Example 4 - Large Priority Family:
    - Household size: 8
    - Base benefit: $20,172 ($12,300 × 1.64)
    - Priority status: Yes (high energy burden)
    - Adjusted benefit: $20,172 × 1.2 = $24,206.40
    - Final benefit: $12,300 (capped at maximum)
    
    Example 5 - Ineligible Household:
    - Household size: 4
    - Income: $75,000 (over 150% FPG)
    - No categorical eligibility
    - Base benefit calculation: $12,300
    - Final benefit: $0 (not eligible)
    
    Benefit Limits:
    - Minimum: $1 (ensures all eligible households receive assistance)
    - Maximum: $12,300 (annual cap per household)
    
    Edge Cases:
    - Very large households with priority status often hit the maximum cap
    - Minimum benefit ensures even minimal calculations result in assistance
    - Benefits are annual amounts, not monthly
    
    Related variables:
    - tx_liheap_base_benefit: Calculates size-adjusted base amount
    - tx_liheap_priority_group: Determines 20% multiplier eligibility
    - tx_liheap_eligible: Gates benefit payment
    """
    reference = [
        "https://www.tdhca.texas.gov/sites/default/files/2023-10/FY2024-LIHEAP-State-Plan.pdf",
        "42 U.S.C. 8624(f) - Priority households",
        "Texas Administrative Code Title 10, Part 1, Chapter 5, Section 5.307"
    ]
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.tdhca.liheap

        # Check eligibility per 42 U.S.C. 8624(b)
        eligible = spm_unit("tx_liheap_eligible", period)

        # Get base benefit calculated from household size
        # Per Texas State Plan Section 4.2: Benefit Matrix
        base_benefit = spm_unit("tx_liheap_base_benefit", period)

        # Check priority group status per 42 U.S.C. 8624(b)(2)(B)
        # Priority households receive additional assistance
        is_priority = spm_unit("tx_liheap_priority_group", period)

        # Apply priority multiplier per Texas State Plan Section 4.3
        # Priority households receive 20% increase in benefits
        adjusted_benefit = where(
            is_priority,
            base_benefit * p.priority_benefit_multiplier,
            base_benefit,
        )

        # Apply minimum and maximum limits per State Plan Section 4.4
        # Ensures all eligible households receive meaningful assistance
        final_benefit = clip(
            adjusted_benefit, p.minimum_benefit, p.maximum_benefit
        )

        # Return benefit only if eligible
        # Non-eligible households receive $0
        return where(eligible, final_benefit, 0)
