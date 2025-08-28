from policyengine_us.model_api import *


class tx_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Texas LIHEAP eligible"
    documentation = """
    Determines overall eligibility for Texas LIHEAP (Low Income Home Energy Assistance Program).
    
    Eligibility Requirements (42 U.S.C. 8624):
    1. Income at or below 150% of Federal Poverty Guidelines, OR
    2. Categorical eligibility through SNAP, TANF, or SSI participation
    3. Must have utility expenses (heating or cooling costs)
    
    Example 1 - Income Eligible Family:
    - Family of 3 with annual income of $35,000
    - FPG for 3-person household (2024): $25,820
    - Income limit: $25,820 × 1.5 = $38,730
    - Income test: $35,000 ≤ $38,730 = TRUE
    - Has utility expenses: $200/month = TRUE
    - Result: ELIGIBLE (meets income test and has utility expenses)
    
    Example 2 - Categorically Eligible Individual:
    - Single person receiving SSI ($914/month)
    - Annual income: $10,968 (below 150% FPG)
    - SSI recipient = categorically eligible
    - Has utility expenses: $150/month = TRUE
    - Result: ELIGIBLE (categorically eligible through SSI)
    
    Example 3 - Over Income Household:
    - Family of 4 with income of $65,000
    - FPG for 4-person household: $31,200
    - Income limit: $31,200 × 1.5 = $46,800
    - Income test: $65,000 > $46,800 = FALSE
    - Not receiving SNAP/TANF/SSI = FALSE
    - Result: INELIGIBLE (exceeds income limit, no categorical eligibility)
    
    Related variables:
    - tx_liheap_income_eligible: Tests household income against 150% FPG
    - tx_liheap_categorical_eligible: Checks SNAP/TANF/SSI participation
    - tx_liheap_regular_benefit: Calculates benefit amount if eligible
    """
    reference = [
        "https://www.tdhca.texas.gov/sites/default/files/2023-10/FY2024-LIHEAP-State-Plan.pdf",
        "42 U.S.C. 8624 - LIHEAP Eligibility Requirements",
        "45 CFR 96.85 - Income eligibility for LIHEAP"
    ]
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Check income eligibility per 45 CFR 96.85
        # Must be at or below 150% of Federal Poverty Guidelines
        income_eligible = spm_unit("tx_liheap_income_eligible", period)

        # Check categorical eligibility per 42 U.S.C. 8624(b)(2)(A)
        # Households receiving SNAP, TANF, or SSI are categorically eligible
        # Need to get a month from the year period to check categorical eligibility
        categorical_eligible = spm_unit(
            "tx_liheap_categorical_eligible", period.first_month
        )

        # Check if household has utility expenses per Texas State Plan Section 2.3
        # Must have heating or cooling costs to qualify for assistance
        has_utility_expense = spm_unit("utility_expense", period) > 0

        # Eligible if either income eligible OR categorically eligible, AND has utility expenses
        # Per 42 U.S.C. 8624(b)(2): "The State may not exclude households...solely on the basis of income"
        return (income_eligible | categorical_eligible) & has_utility_expense
