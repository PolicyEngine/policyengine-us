from policyengine_us.model_api import *


class tx_liheap_priority_group(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Texas LIHEAP priority group household"
    documentation = """
    Determines if household qualifies for priority group status and enhanced benefits.
    
    Priority Group Criteria (42 U.S.C. 8624(b)(2)(B)):
    Federal law requires states to provide priority assistance to vulnerable households.
    Texas defines priority groups as households with:
    
    1. Elderly Members (60+ years old)
       - At least one household member aged 60 or older
       - Recognizes increased vulnerability to extreme temperatures
    
    2. Disabled Members
       - At least one member receiving disability benefits
       - Includes SSI disability, SSDI, or other disability income
    
    3. Young Children (Under 6 years old)
       - At least one child under age 6
       - Addresses health risks for young children
    
    4. High Energy Burden (>10% of income on utilities)
       - Utility expenses exceed 10% of household income
       - Targets households most impacted by energy costs
    
    Priority Benefits:
    - Receive 20% increase in regular benefit amount
    - First in line during funding shortages
    - May qualify for crisis assistance
    
    Example 1 - Elderly Priority Household:
    - Couple, ages 65 and 63
    - Check: Has member 60+ = TRUE
    - Result: PRIORITY GROUP (elderly member)
    - Benefit impact: Base benefit × 1.2
    
    Example 2 - Young Child Priority:
    - Family with 3-year-old and 8-year-old
    - Check: Has child under 6 = TRUE (3-year-old)
    - Result: PRIORITY GROUP (young child)
    - Benefit impact: Base benefit × 1.2
    
    Example 3 - High Energy Burden Priority:
    - Single person, income $1,200/month
    - Utility costs: $180/month
    - Energy burden: $180/$1,200 = 15%
    - Check: 15% > 10% threshold = TRUE
    - Result: PRIORITY GROUP (high energy burden)
    - Benefit impact: Base benefit × 1.2
    
    Example 4 - Multiple Priority Factors:
    - Disabled veteran (age 45) with 5-year-old child
    - Check disabled: TRUE
    - Check young child: TRUE
    - Result: PRIORITY GROUP (multiple qualifying factors)
    - Benefit impact: Base benefit × 1.2 (not cumulative)
    
    Example 5 - Non-Priority Household:
    - Working couple, ages 35 and 37, no children
    - Energy burden: 6% of income
    - No disabilities
    - Result: NOT PRIORITY GROUP
    - Benefit impact: Base benefit × 1.0
    
    Edge Cases:
    - Multiple priority factors don't stack (still 20% increase)
    - Age is checked at start of benefit year
    - Temporary disabilities may qualify if receiving benefits
    
    Related variables:
    - tx_liheap_has_elderly_member: Tests for 60+ members
    - tx_liheap_has_disabled_member: Tests for disability status
    - tx_liheap_has_young_child: Tests for children under 6
    - tx_liheap_high_energy_burden: Tests utility cost burden
    """
    reference = [
        "https://www.tdhca.texas.gov/sites/default/files/2023-10/FY2024-LIHEAP-State-Plan.pdf",
        "42 U.S.C. 8624(b)(2)(B) - Priority for vulnerable households",
        "Texas Administrative Code Title 10, Chapter 5, Section 5.306"
    ]
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Check all priority group criteria per 42 U.S.C. 8624(b)(2)(B)
        # Federal law requires priority for vulnerable populations
        
        # Elderly households per State Plan Section 3.4.1
        has_elderly = spm_unit("tx_liheap_has_elderly_member", period)
        
        # Disabled households per State Plan Section 3.4.2
        has_disabled = spm_unit("tx_liheap_has_disabled_member", period)
        
        # Households with young children per State Plan Section 3.4.3
        has_young_child = spm_unit("tx_liheap_has_young_child", period)
        
        # High energy burden households per State Plan Section 3.4.4
        high_energy_burden = spm_unit("tx_liheap_high_energy_burden", period)

        # Household is priority if it meets ANY of the criteria
        # Multiple criteria don't provide additional benefits
        return (
            has_elderly | has_disabled | has_young_child | high_energy_burden
        )
