from policyengine_us.model_api import *


class form_4952_investment_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Form 4952 investment income"
    unit = USD
    definition_period = YEAR
    documentation = """
    Form 4952 line 4h: "Investment income. Add lines 4c, 4f, and 4g."
    Line 4c is "Subtract line 4b from line 4a" and line 4f is "Subtract
    line 4e from line 4d". Thus ordinary investment income and net gains
    other than net capital gain count automatically; qualified dividends
    and net capital gain count only to the extent elected on line 4g.
    """
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/163#d_4_B",
        "https://www.irs.gov/pub/irs-pdf/f4952.pdf",
    ]

    def formula(tax_unit, period, parameters):
        gross_income = tax_unit("form_4952_gross_investment_income", period)
        qualified_dividends = tax_unit("form_4952_qualified_dividends", period)
        net_gain = tax_unit("form_4952_net_investment_gain", period)
        net_capital_gain = tax_unit("form_4952_net_capital_gain", period)
        election = tax_unit("form_4952_elected_investment_income", period)
        return (
            gross_income - qualified_dividends + net_gain - net_capital_gain + election
        )
