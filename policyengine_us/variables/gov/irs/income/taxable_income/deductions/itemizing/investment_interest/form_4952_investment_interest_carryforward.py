from policyengine_us.model_api import *


class form_4952_investment_interest_carryforward(Variable):
    value_type = float
    entity = TaxUnit
    label = "Form 4952 disallowed investment interest carryforward"
    unit = USD
    definition_period = YEAR
    documentation = """
    Form 4952 line 7: "Disallowed investment interest expense to be carried
    forward to 2026. Subtract line 6 from line 3. If zero or less, enter -0-."
    Section 163(d)(2) treats disallowed interest as "investment interest
    paid or accrued by the taxpayer in the succeeding taxable year".
    This variable reports the current-year amount available to carry
    forward; prior-year carryforwards (line 2) have no input and do not
    automatically enter a later year's calculation.
    """
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/163#d_2",
        "https://www.irs.gov/pub/irs-pdf/f4952.pdf",
    ]

    def formula(tax_unit, period, parameters):
        interest = tax_unit("form_4952_total_investment_interest_expense", period)
        net_income = tax_unit("form_4952_net_investment_income", period)
        return max_(0, interest - net_income)
