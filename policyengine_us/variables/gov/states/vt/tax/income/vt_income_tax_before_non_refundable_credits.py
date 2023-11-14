from policyengine_us.model_api import *


class vt_income_tax_before_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont income tax before non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = (
        "https://casetext.com/statute/vermont-statutes/title-32-taxation-and-finance/chapter-151-income-taxes/subchapter-002-taxation-of-individuals-trusts-and-estates/section-5822-tax-on-income-of-individuals-estates-and-trusts",  # Vermont §5822. Tax on income of individuals, estates, and trusts (a)
        "https://tax.vermont.gov/sites/tax/files/documents/RateSched-2021.pdf#page=1",  # Vermont 2021 Income Tax Rate Schedules
        "https://tax.vermont.gov/sites/tax/files/documents/RateSched-2022.pdf#page=1",  # Vermont 2022 Income Tax Return Booklet Forms and Instructions
    )

    def formula(tax_unit, period, parameters):
        income = tax_unit("vt_taxable_income", period)
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        p = parameters(period).gov.states.vt.tax.income.rates
        income_tax = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.SEPARATE,
                filing_status == status.WIDOW,
                filing_status == status.HEAD_OF_HOUSEHOLD,
            ],
            [
                p.single.calc(income),
                p.joint.calc(income),
                p.separate.calc(income),
                p.widow.calc(income),
                p.head_of_household.calc(income),
            ],
        )
        # If AGI is bigger than a threshold, then we need to further compare a percentage
        # of Adjusted Gross Income less interest from U.S. obligations and the initial Tax
        # Rate Schedule calculation.
        # The reduction of AGI by U.S. obligations is mentioned only in the tax forms, but
        # not in the legal code (Vermont §5822 (a)(6)).
        federal_agi = tax_unit("adjusted_gross_income", period)
        minimum_tax_eligible = (
            federal_agi > p.alternative_minimum_tax.income_threshold
        )
        us_govt_interest = tax_unit("us_govt_interest", period)
        alt_minimum_tax = max_(
            (p.alternative_minimum_tax.rate * federal_agi) - us_govt_interest,
            0,
        )
        return where(
            minimum_tax_eligible,
            max_(alt_minimum_tax, income_tax),
            income_tax,
        )
