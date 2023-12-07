from policyengine_us.model_api import *


class vt_normal_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont normal income tax before non-refundable credits"
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
        return select(
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
