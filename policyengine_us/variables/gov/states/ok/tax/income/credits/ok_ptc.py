from policyengine_us.model_api import *


class ok_ptc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma property tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        # 2025 Form 538-H (Property Tax Credit form)
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/538-H.pdf",
    )
    defined_for = StateCode.OK
    documentation = """
    Oklahoma Property Tax Credit for seniors and disabled individuals.

    This refundable credit helps low-income elderly and disabled homeowners
    offset their property tax burden. The credit equals the excess property
    tax paid above 1% of gross household income, up to a maximum of $200.

    Eligibility requirements (must meet ALL):
    1. Age requirement: Head OR spouse must be age 65 or older, OR
       head must be totally disabled
    2. Income requirement: Gross household income must be $12,000 or less
    3. Must have paid real estate taxes on Oklahoma homestead

    Credit calculation:
    - Excess property tax = Property taxes paid - (1% * Gross income)
    - Credit = min($200, max($0, Excess property tax))

    Example 1 - Full credit:
    - Age: 70 (eligible)
    - Gross income: $10,000 (eligible, under $12,000 limit)
    - Property taxes paid: $500
    - 1% of income: $10,000 * 0.01 = $100
    - Excess tax: $500 - $100 = $400
    - Credit: min($200, $400) = $200

    Example 2 - Partial credit:
    - Age: 66 (eligible)
    - Gross income: $11,000 (eligible)
    - Property taxes paid: $200
    - 1% of income: $11,000 * 0.01 = $110
    - Excess tax: $200 - $110 = $90
    - Credit: min($200, $90) = $90

    Example 3 - No credit (income too high):
    - Age: 68 (eligible)
    - Gross income: $15,000 (NOT eligible, over $12,000 limit)
    - Credit: $0

    Note: This is a refundable credit claimed on Form 538-H.
    """

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ok.tax.income.credits.property_tax
        # Step 1: Check age/disability eligibility
        elderly_head = tax_unit("age_head", period) >= p.age_minimum
        elderly_spouse = tax_unit("age_spouse", period) >= p.age_minimum
        disabled_head = tax_unit("head_is_disabled", period)
        unit_eligible = elderly_head | elderly_spouse | disabled_head
        # Step 2: Check income eligibility (gross income <= $12,000)
        income = tax_unit("ok_gross_income", period)
        income_eligible = income <= p.income_limit
        eligible = unit_eligible & income_eligible
        # Step 3: Calculate credit if eligible
        # Credit = min($200, property_tax - 1% * income)
        tax = add(tax_unit, period, ["real_estate_taxes"])
        excess_property_tax = max_(0, tax - p.income_fraction * income)
        return eligible * min_(p.maximum_credit, excess_property_tax)
