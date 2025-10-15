"""
Connecticut TFA family cap benefit reduction.
"""

from policyengine_us.model_api import *


class ct_tfa_family_cap_reduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut TFA family cap reduction amount"
    definition_period = MONTH
    defined_for = StateCode.CT
    unit = USD
    documentation = (
        "The amount by which the Connecticut TFA benefit is reduced due to the "
        "partial family cap policy.\n\n"
        "Connecticut's Partial Family Cap:\n"
        "  - Applies to children born within 10 months of TFA application\n"
        "  - Reduces benefit increase by 50% for these children\n"
        "  - Connecticut is the only state with a partial (not full) family cap\n"
        "  - Exceptions: Children conceived by rape/incest, first child to minor parent\n\n"
        "Calculation Method:\n"
        "  1. Determine payment standard for current household size\n"
        "  2. Determine payment standard for household size minus one\n"
        "  3. Calculate increment: current - previous\n"
        "  4. Apply 50% reduction to increment\n\n"
        "Example 1 - Family cap applies (Region A, 2→3 persons):\n"
        "  - Previous payment standard (size 2): $563/month\n"
        "  - Current payment standard (size 3): $698/month\n"
        "  - Full increment: $698 - $563 = $135\n"
        "  - Family cap reduction (50%): $135 × 0.50 = $67.50\n"
        "  - Net benefit increase: $135 - $67.50 = $67.50\n"
        "  - Effective benefit: $563 + $67.50 = $630.50/month\n\n"
        "Example 2 - Family cap applies (Region B, 3→4 persons):\n"
        "  - Previous payment standard (size 3): $597/month\n"
        "  - Current payment standard (size 4): $701/month\n"
        "  - Full increment: $701 - $597 = $104\n"
        "  - Family cap reduction (50%): $104 × 0.50 = $52\n"
        "  - Net benefit increase: $104 - $52 = $52\n"
        "  - Effective benefit: $597 + $52 = $649/month\n\n"
        "Example 3 - Family cap does NOT apply (child born 12 months after application):\n"
        "  - Previous payment standard (size 2): $563/month\n"
        "  - Current payment standard (size 3): $698/month\n"
        "  - Family cap reduction: $0 (outside 10-month window)\n"
        "  - Full benefit increase received: $698 - $563 = $135\n"
        "  - Effective benefit: $698/month\n\n"
        "Related Variables:\n"
        "  - ct_tfa_family_cap_applies: Determines if reduction applies\n"
        "  - ct_tfa_payment_standard: Base benefit amounts by size\n"
        "  - ct_tfa_assistance_unit_size: Current household size\n"
        "  - ct_tfa: Final benefit calculation\n\n"
        "Policy Rationale:\n"
        "Connecticut's partial family cap (50% reduction) is less restrictive than "
        "other states' full family caps. It aims to discourage additional births "
        "while receiving TFA while still providing some increased support for the "
        "new child."
    )
    reference = (
        "Conn. Gen. Stat. § 17b-688b (Family Cap Authorization); "
        "Connecticut General Assembly OLR Report 98-R-0058 (Family Cap Analysis); "
        "SSA POMS SI BOS00830.403 - TANF - Connecticut, Family Cap Policy; "
        "https://www.cga.ct.gov/PS98/rpt/olr/htm/98-R-0058.htm; "
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0500830403BOS"
    )

    def formula(spm_unit, period, parameters):
        # Consolidate parameter access for better performance
        p_tfa = parameters(period).gov.states.ct.dss.tfa
        p_family_cap = p_tfa.family_cap
        p_payment = p_tfa.payment_standard

        # Check if family cap applies to this household
        # Returns True if child born within 10 months of application
        # (subject to exceptions for rape/incest, minor parent's first child)
        family_cap_applies = spm_unit("ct_tfa_family_cap_applies", period)

        # Calculate the reduction amount when family cap applies
        # The family cap reduces the benefit increase for additional children
        # born within 10 months of TFA application by 50%
        # Conn. Gen. Stat. § 17b-688b

        # Step 1: Get household characteristics
        region = spm_unit("ct_tfa_region_str", period.this_year)
        size = spm_unit("ct_tfa_assistance_unit_size", period.this_year)

        # Step 2: Prepare size values for parameter lookup
        # Payment standards are defined up to household size 20
        capped_size = min_(size, 20)
        capped_size_minus_one = max_(min_(size - 1, 20), 1)

        # Convert sizes to strings to match parameter file structure
        # Parameters use string keys: "1", "2", "3", etc.
        size_str = capped_size.astype(str)
        size_minus_one_str = capped_size_minus_one.astype(str)

        # Step 3: Determine household region
        region_a = region == "A"
        region_b = region == "B"
        # Region C is default if not A or B

        # Step 4: Look up payment standard for CURRENT household size
        # Example: Region A, size 3 = $698
        payment_current_a = p_payment.region_a[size_str]
        payment_current_b = p_payment.region_b[size_str]
        payment_current_c = p_payment.region_c[size_str]
        payment_current = where(
            region_a,
            payment_current_a,
            where(region_b, payment_current_b, payment_current_c),
        )

        # Step 5: Look up payment standard for PREVIOUS household size
        # (before the additional child that triggers family cap)
        # Example: Region A, size 2 = $563
        payment_previous_a = p_payment.region_a[size_minus_one_str]
        payment_previous_b = p_payment.region_b[size_minus_one_str]
        payment_previous_c = p_payment.region_c[size_minus_one_str]
        payment_previous = where(
            region_a,
            payment_previous_a,
            where(region_b, payment_previous_b, payment_previous_c),
        )

        # Step 6: Calculate the benefit increment for the additional child
        # Example: $698 - $563 = $135
        increment = payment_current - payment_previous

        # Step 7: Apply the 50% reduction to the increment
        # reduction_percentage = 0.5 (50%)
        # Example: $135 × 0.50 = $67.50
        reduction = increment * p_family_cap.reduction_percentage

        # Step 8: Return reduction only if family cap applies, otherwise $0
        # This reduction will be subtracted from the base benefit in ct_tfa.py
        return where(family_cap_applies, reduction, 0)
