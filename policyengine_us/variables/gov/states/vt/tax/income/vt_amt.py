from policyengine_us.model_api import *


class vt_amt(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont alternative minimum tax (AMT)"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://casetext.com/statute/vermont-statutes/title-32-taxation-and-finance/chapter-151-income-taxes/subchapter-002-taxation-of-individuals-trusts-and-estates/section-5822-tax-on-income-of-individuals-estates-and-trusts",  # Vermont §5822. Tax on income of individuals, estates, and trusts (a)
        "https://tax.vermont.gov/sites/tax/files/documents/RateSched-2021.pdf#page=1",  # Vermont 2021 Income Tax Rate Schedules
        "https://tax.vermont.gov/sites/tax/files/documents/RateSched-2022.pdf#page=1",  # Vermont 2022 Income Tax Return Booklet Forms and Instructions
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.tax.income.rates
        # If AGI is bigger than a threshold, then we need to further compare a percentage
        # of Adjusted Gross Income less interest from U.S. obligations and the initial Tax
        # Rate Schedule calculation.
        # The reduction of AGI by U.S. obligations is mentioned only in the tax forms, but
        # not in the legal code (Vermont §5822 (a)(6)).
        federal_agi = tax_unit("adjusted_gross_income", period)
        us_govt_interest = tax_unit("us_govt_interest", period)
        amt_rate = p.amt.calc(federal_agi)
        base_amt = amt_rate * federal_agi
        return max_(base_amt - us_govt_interest, 0)
