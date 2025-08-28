from policyengine_us.model_api import *


class tx_liheap_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "Texas LIHEAP countable monthly income"
    documentation = """
    Calculates total monthly countable household income for Texas LIHEAP eligibility.
    
    Countable Income Sources (45 CFR 96.85):
    Federal regulations require counting most sources of household income:
    
    1. Earned Income:
       - Employment wages and salaries
       - Self-employment income (net of business expenses)
    
    2. Unearned Income:
       - Social Security benefits (retirement, disability, survivors)
       - Supplemental Security Income (SSI)
       - TANF cash assistance
       - Unemployment compensation
       - Veterans benefits
       - Workers compensation
       - Pension and retirement income
    
    Income Calculation:
    - Annual income sources are divided by 12 for monthly average
    - All household members' income is included
    - Gross income before taxes (except self-employment uses net)
    
    Example 1 - Working Family:
    - Parent 1 employment: $36,000/year = $3,000/month
    - Parent 2 employment: $24,000/year = $2,000/month
    - Child support: Not counted (not in list)
    - Total monthly income: $5,000
    
    Example 2 - Retired Couple:
    - Person 1 Social Security: $1,400/month
    - Person 2 Social Security: $1,200/month
    - Person 1 pension: $6,000/year = $500/month
    - Total monthly income: $3,100
    
    Example 3 - Mixed Income Household:
    - Adult employment: $30,000/year = $2,500/month
    - SSI for disabled child: $914/month
    - TANF assistance: $300/month
    - Total monthly income: $3,714
    
    Example 4 - Unemployed Individual:
    - Unemployment benefits: $400/week × 52 = $20,800/year = $1,733/month
    - SNAP benefits: Not counted (in-kind benefit)
    - Total monthly income: $1,733
    
    Example 5 - Self-Employed Household:
    - Self-employment net income: $48,000/year = $4,000/month
    - Social Security: $18,000/year = $1,500/month
    - Total monthly income: $5,500
    
    Excluded Income (not counted):
    - SNAP benefits (food assistance)
    - Housing assistance payments
    - Energy assistance from other programs
    - Child support payments (in Texas)
    - Gifts and loans
    
    Special Considerations:
    - Uses 12-month average to smooth seasonal variations
    - Self-employment uses net income after business expenses
    - All adult and child income in household is counted
    
    Related variables:
    - employment_income: Wages from employment
    - self_employment_income: Net business income
    - social_security: All SS benefit types
    - tx_liheap_income_eligible: Uses this for eligibility test
    """
    reference = [
        "https://www.tdhca.texas.gov/sites/default/files/2023-10/FY2024-LIHEAP-State-Plan.pdf",
        "45 CFR 96.85(b) - Income to be counted",
        "Texas Administrative Code Title 10, Chapter 5, Section 5.308"
    ]
    defined_for = StateCode.TX
    unit = USD

    def formula(spm_unit, period, parameters):
        # Get all people in the SPM unit per 45 CFR 96.85(b)
        person = spm_unit.members
        
        # Get annual period once for all annual income sources
        annual_period = period.this_year
        
        # Combine all annual income sources in a single operation
        # This reduces the number of person() calls and improves performance
        annual_income_sources = [
            "employment_income",           # 45 CFR 96.85(b)(1)
            "self_employment_income",      # 45 CFR 96.85(b)(2)
            "social_security",             # 45 CFR 96.85(b)(3)
            "ssi",                         # 45 CFR 96.85(b)(4)
            "unemployment_compensation",   # 45 CFR 96.85(b)(5)
            "veterans_benefits",           # 45 CFR 96.85(b)(6)
            "workers_compensation",        # 45 CFR 96.85(b)(7)
            "taxable_pension_income",      # 45 CFR 96.85(b)(8)
        ]
        
        # Calculate total annual income from all sources efficiently
        total_annual_income = 0
        for source in annual_income_sources:
            income = person(source, annual_period)
            total_annual_income += spm_unit.sum(income)
        
        # Convert annual to monthly once
        months_in_year = p.months_in_year
        total_monthly_from_annual = total_annual_income / months_in_year
        
        # TANF benefits per State Plan Section 3.2
        # Already calculated as monthly amount
        tanf = spm_unit("tanf", period)
        
        # Calculate total monthly income per State Plan formula
        return total_monthly_from_annual + tanf
