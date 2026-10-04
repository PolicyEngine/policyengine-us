from policyengine_us.model_api import *


class form_4952_net_investment_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Form 4952 net investment income"
    unit = USD
    definition_period = YEAR
    documentation = """
    Form 4952 line 6: "Net investment income. Subtract line 5 from line 4h.
    If zero or less, enter -0-." This implements 163(d)(4)(A)'s excess of
    investment income over investment expenses for the interest limit,
    separately from net_investment_income used for the NIIT.
    """
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/163#d_4_A",
        "https://www.irs.gov/pub/irs-pdf/f4952.pdf",
    ]

    def formula(tax_unit, period, parameters):
        income = tax_unit("form_4952_investment_income", period)
        expenses = tax_unit("form_4952_investment_expenses", period)
        return max_(0, income - expenses)
