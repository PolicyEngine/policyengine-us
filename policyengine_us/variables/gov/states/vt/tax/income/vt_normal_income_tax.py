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
        p = parameters(period).gov.states.vt.tax.income.rates
        return select_filing_status_value(
            filing_status,
            p,
            income,
        )
