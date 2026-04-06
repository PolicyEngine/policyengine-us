from policyengine_us.model_api import *


class ok_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma income tax before credits"
    unit = USD
    definition_period = YEAR
    reference = (
        # 2025 Form 511-NR instructions, page 38 (tax tables)
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-NR-Pkt.pdf#page=38",
        # Oklahoma Statutes 68 O.S. Section 2355 - Tax rates
        "https://www.oscn.net/applications/oscn/DeliverDocument.asp?CiteID=92565",
    )
    defined_for = StateCode.OK
    documentation = """
    Oklahoma income tax computed using graduated marginal rate brackets.
    The tax is calculated based on Oklahoma taxable income and filing status.

    2025 Tax Rate Structure (Single filers):
    - 0.25% on first $1,000
    - 0.75% on $1,000 to $2,500
    - 1.75% on $2,500 to $3,750
    - 2.75% on $3,750 to $4,900
    - 3.75% on $4,900 to $7,200
    - 4.75% on income over $7,200

    Example calculation for single filer with $50,000 taxable income (2025):
    - $1,000 * 0.0025 = $2.50
    - $1,500 * 0.0075 = $11.25
    - $1,250 * 0.0175 = $21.88
    - $1,150 * 0.0275 = $31.63
    - $2,300 * 0.0375 = $86.25
    - $42,800 * 0.0475 = $2,033.00
    - Total tax: $2,186.51

    Note: Joint filers and surviving spouses use doubled bracket thresholds.
    Head of household uses intermediate thresholds between single and joint.
    """

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        taxable_income = tax_unit("ok_taxable_income", period)
        p = parameters(period).gov.states.ok.tax.income.rates
        # Apply the appropriate rate schedule based on filing status
        return select(
            [
                filing_status == statuses.SINGLE,
                filing_status == statuses.SEPARATE,
                filing_status == statuses.JOINT,
                filing_status == statuses.SURVIVING_SPOUSE,
                filing_status == statuses.HEAD_OF_HOUSEHOLD,
            ],
            [
                p.single.calc(taxable_income),
                p.separate.calc(taxable_income),
                p.joint.calc(taxable_income),
                p.surviving_spouse.calc(taxable_income),
                p.head_of_household.calc(taxable_income),
            ],
        )
