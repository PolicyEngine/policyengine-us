"""
Connecticut TFA countable unearned income after exclusions.
"""

from policyengine_us.model_api import *


class ct_tfa_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut TFA countable unearned income"
    definition_period = MONTH
    defined_for = StateCode.CT
    unit = USD
    documentation = (
        "Connecticut TFA unearned income after applying exclusions.\n\n"
        "Treatment of Unearned Income:\n"
        "  - Most unearned income: Counted dollar-for-dollar\n"
        "  - Child support: First $50/month passed through and excluded\n"
        "  - SSI: Fully excluded (not included in gross unearned income)\n\n"
        "Example 1 - Child support only ($75/month):\n"
        "  - Gross unearned income: $75 (child support)\n"
        "  - Child support received: $75\n"
        "  - Child support passthrough: min($75, $50) = $50\n"
        "  - Countable unearned income: $75 - $50 = $25\n"
        "  - Note: First $50 is passed through to family, not counted\n\n"
        "Example 2 - Child support ($30/month):\n"
        "  - Gross unearned income: $30 (child support)\n"
        "  - Child support received: $30\n"
        "  - Child support passthrough: min($30, $50) = $30\n"
        "  - Countable unearned income: $30 - $30 = $0\n"
        "  - Note: All child support excluded (under $50 limit)\n\n"
        "Example 3 - Child support ($150/month) + other income ($200/month):\n"
        "  - Gross unearned income: $350 (child support + other)\n"
        "  - Child support received: $150\n"
        "  - Child support passthrough: min($150, $50) = $50\n"
        "  - Countable unearned income: $350 - $50 = $300\n"
        "  - Breakdown: ($150 - $50) + $200 = $300\n\n"
        "Example 4 - SSI recipient ($900/month SSI, $100 other):\n"
        "  - SSI: $900 (excluded from gross unearned, not counted)\n"
        "  - Gross unearned income: $100 (SSI already excluded)\n"
        "  - Child support passthrough: $0 (no child support)\n"
        "  - Countable unearned income: $100 - $0 = $100\n\n"
        "Related Variables:\n"
        "  - ct_tfa_gross_unearned_income: Starting point (SSI already excluded)\n"
        "  - child_support_received: Used to calculate $50 passthrough\n"
        "  - ct_tfa_countable_earned_income: Combined to get total countable income\n\n"
        "Note: The $50 child support passthrough helps ensure child support "
        "payments benefit the family rather than just reducing TFA benefits."
    )
    reference = (
        "SSA POMS SI BOS00830.403 - TANF - Connecticut, Child Support Provisions; "
        "Connecticut DSS Uniform Policy Manual Section 8030 (Income Treatment); "
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0500830403BOS; "
        "https://portal.ct.gov/DSS/Lists/Uniform-Policy-Manual"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.tfa

        # Get gross unearned income (SSI already excluded)
        # This includes: child support, unemployment, Social Security,
        # pensions, interest, dividends, etc.
        gross_unearned = spm_unit("ct_tfa_gross_unearned_income", period)

        # Apply child support passthrough exclusion
        # Connecticut passes through the first $50/month of child support
        # to the TFA household, encouraging non-custodial parents to pay
        # support while ensuring the payment benefits the child
        # SSA POMS SI BOS00830.403
        child_support = spm_unit("child_support_received", period)

        # Get passthrough amount from parameters ($50/month)
        passthrough = p.income_disregards.child_support_passthrough

        # Exclude the lesser of actual child support or $50
        # Example: If child support = $75, exclude $50
        # Example: If child support = $30, exclude $30
        child_support_exclusion = min_(child_support, passthrough)

        # Calculate countable unearned income
        # Subtract child support exclusion from gross unearned
        # Cannot be negative (use max_ to ensure zero floor)
        countable = max_(gross_unearned - child_support_exclusion, 0)

        return countable
