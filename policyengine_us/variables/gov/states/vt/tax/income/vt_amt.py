from policyengine_us.model_api import *


class vt_amt(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont alternative minimum tax (AMT)"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://legislature.vermont.gov/statutes/section/32/151/05822",  # Vermont §5822. Tax on income of individuals, estates, and trusts (a)
        "https://tax.vermont.gov/sites/tax/files/documents/RateSched-2021.pdf#page=1",  # Vermont 2021 Income Tax Rate Schedules
        "https://tax.vermont.gov/sites/tax/files/documents/RateSched-2022.pdf#page=1",  # Vermont 2022 Income Tax Return Booklet Forms and Instructions
        "https://www.law.cornell.edu/uscode/text/45/231m#a",  # No state tax on Railroad Retirement Act annuities
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
        # 45 U.S.C. 231m(a) bars any state tax on Railroad Retirement Act
        # annuities, so the percentage applies to federal AGI less the
        # benefits it includes. The threshold test still uses federal AGI,
        # as section 5822(a)(6) writes it.
        railroad = add(tax_unit, period, ["taxable_railroad_benefits"])
        amt_rate = p.amt.calc(federal_agi)
        base_amt = amt_rate * max_(federal_agi - railroad, 0)
        return max_(base_amt - us_govt_interest, 0)
