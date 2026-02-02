from policyengine_us.model_api import *


class ok_stc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma sales tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        # 2025 Form 538-S (Sales Tax Relief Credit form)
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/538-S.pdf",
    )
    defined_for = StateCode.OK
    documentation = """
    Oklahoma Sales Tax Relief Credit.

    This refundable credit provides $40 per household member to help offset
    sales taxes paid by low-income Oklahoma residents.

    Eligibility has TWO alternative pathways:

    Pathway 1 - Low income (no other requirements):
    - Gross household income <= $20,000
    - Not receiving TANF benefits

    Pathway 2 - Moderate income with qualifying circumstances:
    - Gross household income <= $50,000
    - AND at least one of:
      * Has dependents, OR
      * Head or spouse is age 65+, OR
      * Head or spouse is disabled
    - Not receiving TANF benefits

    Credit calculation:
    - $40 per person in the tax unit (head, spouse, and dependents)

    Example 1 - Pathway 1 (low income):
    - Gross income: $18,000 (eligible under $20,000 limit)
    - Household size: 3 (head + spouse + 1 child)
    - Credit: 3 * $40 = $120

    Example 2 - Pathway 2 (moderate income, elderly):
    - Gross income: $35,000 (over $20,000 but under $50,000)
    - Head age: 67 (qualifies as elderly)
    - Household size: 2
    - Credit: 2 * $40 = $80

    Example 3 - Pathway 2 (moderate income, has dependents):
    - Gross income: $45,000 (over $20,000 but under $50,000)
    - Has 2 dependent children (qualifies)
    - Household size: 4
    - Credit: 4 * $40 = $160

    Example 4 - Not eligible:
    - Gross income: $25,000 (over $20,000, so Pathway 1 fails)
    - No dependents, not elderly, not disabled (Pathway 2 fails)
    - Credit: $0

    Note: TANF recipients are NOT eligible for this credit.
    """

    def formula(tax_unit, period, parameters):
        # For details, see Form 538-S in the 511 packets referenced above
        p = parameters(period).gov.states.ok.tax.income.credits.sales_tax
        # Exclusion: TANF recipients are not eligible
        tanf_ineligible = add(tax_unit, period, ["ok_tanf"]) > 0
        # Get gross household income for eligibility tests
        income = tax_unit("ok_gross_income", period)
        # Pathway 1: Low income (gross income <= $20,000)
        income_eligible1 = income <= p.income_limit1
        # Pathway 2: Moderate income with qualifying circumstances
        # Must have dependents, or be elderly (65+), or be disabled
        has_dependents = tax_unit("tax_unit_dependents", period) > 0
        elderly_head_or_spouse = (
            tax_unit("greater_age_head_spouse", period) >= p.age_minimum
        )
        disabled_head_or_spouse = tax_unit(
            "disabled_tax_unit_head_or_spouse", period
        )
        unit_eligible = (
            has_dependents | elderly_head_or_spouse | disabled_head_or_spouse
        )
        # Pathway 2 requires qualifying circumstance AND income <= $50,000
        income_eligible2 = unit_eligible & (income <= p.income_limit2)
        # Overall eligibility: not on TANF AND (Pathway 1 OR Pathway 2)
        eligible = ~tanf_ineligible & (income_eligible1 | income_eligible2)
        # Credit = $40 per person in tax unit
        qualified_exemptions = tax_unit("tax_unit_size", period)
        return eligible * qualified_exemptions * p.amount
