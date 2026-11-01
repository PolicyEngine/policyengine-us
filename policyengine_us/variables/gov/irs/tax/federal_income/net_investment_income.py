from policyengine_us.model_api import *


class net_investment_income(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "net investment income (NII) that is base of the NII Tax (NIIT)"
    documentation = (
        "Net investment income of the head and spouse, the base of the net "
        "investment income tax. Section 1411(a)(1) taxes each individual's "
        "own net investment income, so a tax unit dependent's interest, "
        "dividends, rents, passive income and capital gains go on the "
        "dependent's own Form 8960, as in irs_gross_income. A parent's Form "
        "8960 picks up a child's income only through a Form 8814 election "
        "(Form 8960 line 7), which is not modeled."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/1411#a_1",
        "https://www.law.cornell.edu/uscode/text/26/1411#c",
        "https://www.irs.gov/pub/irs-prior/i8960--2024.pdf#page=11",
        "https://www.irs.gov/pub/irs-pdf/i8814.pdf#page=2",
    )
    unit = USD

    def formula(tax_unit, period, parameters):
        sources = parameters(period).gov.irs.investment.income.sources
        return tax_unit_non_dep_add(tax_unit, period, sources)
