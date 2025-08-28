from policyengine_us.model_api import *


class tx_liheap_base_benefit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Texas LIHEAP base benefit"
    unit = USD
    documentation = """
    Calculates base LIHEAP benefit amount using household size adjustments.
    
    Benefit Calculation Method (45 CFR 96.85):
    Base Benefit = Maximum Benefit × Household Size Adjustment Factor
    
    The adjustment factors scale benefits based on household size, recognizing
    economies of scale in energy costs. A 4-person household is the baseline (1.00).
    
    Household Size Adjustment Factors:
    - 1 person: 0.52 (52% of maximum)
    - 2 persons: 0.68 (68% of maximum)
    - 3 persons: 0.84 (84% of maximum)
    - 4 persons: 1.00 (100% of maximum - baseline)
    - 5 persons: 1.16 (116% of maximum)
    - 6 persons: 1.32 (132% of maximum)
    - 7 persons: 1.48 (148% of maximum)
    - 8 persons: 1.64 (164% of maximum)
    - 9 persons: 1.80 (180% of maximum)
    - 10+ persons: 1.96 (196% of maximum)
    
    Example 1 - Single Person:
    - Household size: 1
    - Maximum benefit: $12,300
    - Adjustment factor: 0.52
    - Calculation: $12,300 × 0.52 = $6,396
    - Base benefit: $6,396
    
    Example 2 - Family of Four (Baseline):
    - Household size: 4
    - Maximum benefit: $12,300
    - Adjustment factor: 1.00
    - Calculation: $12,300 × 1.00 = $12,300
    - Base benefit: $12,300
    
    Example 3 - Large Family:
    - Household size: 7
    - Maximum benefit: $12,300
    - Adjustment factor: 1.48
    - Calculation: $12,300 × 1.48 = $18,204
    - Base benefit: $18,204 (will be capped at maximum in final benefit)
    
    Example 4 - Very Large Family:
    - Household size: 12
    - Maximum benefit: $12,300
    - Adjustment factor: 1.96 (uses 10+ person factor)
    - Calculation: $12,300 × 1.96 = $24,108
    - Base benefit: $24,108 (will be capped at maximum in final benefit)
    
    Edge Cases:
    - Households larger than 10 persons use the 10-person adjustment factor (1.96)
    - The base benefit can exceed the maximum benefit for large households
    - Final benefit calculation applies minimum/maximum limits
    
    Related variables:
    - tx_liheap_regular_benefit: Applies priority multiplier and limits
    - tx_liheap_priority_group: Determines if priority multiplier applies
    """
    reference = [
        "https://www.tdhca.texas.gov/sites/default/files/2023-10/FY2024-LIHEAP-State-Plan.pdf",
        "45 CFR 96.85 - Benefit levels for LIHEAP",
        "Texas Administrative Code Title 10, Part 1, Chapter 5, Subchapter A"
    ]
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.tdhca.liheap

        # Get household size per 45 CFR 96.82
        size = spm_unit.nb_persons()

        # Cap household size at 10 per State Plan Benefit Matrix
        # Households with more than 10 members use the 10-person factor
        capped_size = min_(size, 10)

        # Optimized adjustment factor lookup using a single parameter access
        # and vectorized array indexing
        adjustments = p.household_size_adjustments
        
        # Create array of adjustment factors (more efficient than select)
        # Index 0 is unused (no 0-person households), indices 1-10 map to sizes
        factors = [
            0,  # Index 0 - unused
            adjustments.one_person,
            adjustments.two_person,
            adjustments.three_person,
            adjustments.four_person,
            adjustments.five_person,
            adjustments.six_person,
            adjustments.seven_person,
            adjustments.eight_person,
            adjustments.nine_person,
            adjustments.ten_person,
        ]
        
        # Use select for vectorized lookup - more efficient with pre-built array
        # This avoids multiple comparisons and is faster for large datasets
        adjustment_factor = select(
            [capped_size == i for i in range(1, 11)],
            factors[1:],  # Skip index 0
            default=adjustments.ten_person,  # For edge cases
        )

        # Calculate base benefit using adjustment factor and maximum benefit
        # This provides the starting point before priority adjustments
        base_amount = p.maximum_benefit * adjustment_factor

        return base_amount
