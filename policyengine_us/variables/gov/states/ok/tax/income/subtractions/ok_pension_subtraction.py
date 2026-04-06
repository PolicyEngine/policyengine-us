from policyengine_us.model_api import *


class ok_pension_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma pension subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os68.pdf#page=1012",
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os68.pdf#page=1013",
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2024/511-Pkt-2024.pdf#page=17",
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf#page=17",
    )
    defined_for = StateCode.OK
    documentation = """
    Oklahoma allows a subtraction from AGI for retirement benefits received
    from qualified retirement plans, up to a per-person limit.

    Example calculation for 2025:
    - Head receives $25,000 in pension income
    - Spouse receives $15,000 in pension income
    - Head subtraction: min($10,000, $25,000) = $10,000
    - Spouse subtraction: min($10,000, $15,000) = $10,000
    - Total subtraction: $10,000 + $10,000 = $20,000

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
