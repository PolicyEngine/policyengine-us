from policyengine_us.model_api import *


class ok_pension_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma pension subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        # 2025 Form 511-NR instructions, page 17
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-NR-Pkt.pdf#page=17",
        # HB 2020 increased the limit from $10,000 to $20,000 effective 2024
        "https://www.okhouse.gov/posts/news-20230324_4",
    )
    defined_for = StateCode.OK
    documentation = """
    Oklahoma allows a subtraction from AGI for retirement benefits received
    from qualified retirement plans, up to a per-person limit.

    Legislative history:
    - Prior to 2024: $10,000 per person limit
    - 2024 onwards: $20,000 per person limit (increased by HB 2020)

    Example calculation for 2025:
    - Head receives $25,000 in pension income
    - Spouse receives $15,000 in pension income
    - Head subtraction: min($20,000, $25,000) = $20,000
    - Spouse subtraction: min($20,000, $15,000) = $15,000
    - Total subtraction: $20,000 + $15,000 = $35,000

    Note: The subtraction applies per person, not per tax unit, so married
    couples filing jointly can each claim up to the maximum limit.
    """

    def formula(tax_unit, period, parameters):
        # Get pension income for each person in the tax unit
        pensions = tax_unit.members("taxable_pension_income", period)
        p = parameters(period).gov.states.ok.tax.income.agi.subtractions
        # Each person can subtract up to the pension limit
        # Sum across all tax unit members
        return tax_unit.sum(min_(p.pension_limit, pensions))
