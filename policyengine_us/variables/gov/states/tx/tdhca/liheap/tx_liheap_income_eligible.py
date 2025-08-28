from policyengine_us.model_api import *


class tx_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Texas LIHEAP income eligible"
    documentation = """
    Determines if household meets Texas LIHEAP income eligibility requirements.
    
    Income Test (45 CFR 96.85):
    - Household income must not exceed 150% of Federal Poverty Guidelines
    - Uses gross monthly income annualized for comparison
    - All countable income sources included per federal guidelines
    
    Calculation Formula:
    Annual Income ≤ (FPG for household size × 1.5)
    
    Example 1 - Small Household at Limit:
    - Single person household
    - Monthly income: $1,755 (Social Security)
    - Annual income: $1,755 × 12 = $21,060
    - FPG for 1 person (2024): $15,060
    - Income limit: $15,060 × 1.5 = $22,590
    - Test: $21,060 ≤ $22,590 = TRUE
    - Result: INCOME ELIGIBLE
    
    Example 2 - Large Family Near Limit:
    - 5-person household
    - Monthly employment income: $3,200
    - Annual income: $3,200 × 12 = $38,400
    - FPG for 5 persons (2024): $36,580
    - Income limit: $36,580 × 1.5 = $54,870
    - Test: $38,400 ≤ $54,870 = TRUE
    - Result: INCOME ELIGIBLE
    
    Example 3 - Over Income Household:
    - 3-person household
    - Monthly income: $3,500 (employment + pension)
    - Annual income: $3,500 × 12 = $42,000
    - FPG for 3 persons (2024): $25,820
    - Income limit: $25,820 × 1.5 = $38,730
    - Test: $42,000 > $38,730 = FALSE
    - Result: NOT INCOME ELIGIBLE (may still qualify categorically)
    
    Federal Poverty Guidelines (2024 - 48 contiguous states):
    - 1 person: $15,060
    - 2 persons: $20,440
    - 3 persons: $25,820
    - 4 persons: $31,200
    - Each additional: +$5,380
    
    Related variables:
    - tx_liheap_income: Calculates total countable monthly income
    - spm_unit_fpg: Provides Federal Poverty Guideline for household size
    - tx_liheap_categorical_eligible: Alternative eligibility pathway
    """
    reference = [
        "https://www.tdhca.texas.gov/sites/default/files/2023-10/FY2024-LIHEAP-State-Plan.pdf",
        "45 CFR 96.85 - Income eligibility for LIHEAP assistance",
        "https://aspe.hhs.gov/topics/poverty-economic-mobility/poverty-guidelines"
    ]
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.tdhca.liheap

        # Get household monthly income per Texas State Plan Section 3.2
        # Income calculated as 12-month average for annual determination
        monthly_income = spm_unit("tx_liheap_income", period.first_month)
        months_in_year = p.months_in_year
        annual_income = monthly_income * months_in_year

        # Get household size for FPG determination
        size = spm_unit.nb_persons()

        # Get FPG (Federal Poverty Guidelines) for household
        # Per 45 CFR 96.85(a): States may not set income eligibility above 150% FPG
        fpg = spm_unit("spm_unit_fpg", period)

        # Apply Texas FPG ratio (150% per State Plan Section 3.1)
        # Texas uses maximum allowed federal threshold
        income_limit = fpg * p.income_limit_fpg_ratio

        return annual_income <= income_limit
