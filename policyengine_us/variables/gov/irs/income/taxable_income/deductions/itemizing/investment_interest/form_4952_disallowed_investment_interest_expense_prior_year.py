from policyengine_us.model_api import *


class form_4952_disallowed_investment_interest_expense_prior_year(Variable):
    value_type = float
    entity = TaxUnit
    label = "Form 4952 disallowed investment interest expense from the prior year"
    unit = USD
    definition_period = YEAR
    documentation = """
    Form 4952 line 2: "Disallowed investment interest expense from 2024 Form
    4952, line 7." Section 163(d)(2) treats interest disallowed under the
    limit as "investment interest paid or accrued by the taxpayer in the
    succeeding taxable year". The model does not carry one year's line 7 into
    the next year's simulation, so the prior-year amount is an input. It
    defaults to zero.
    """
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/163#d_2",
        "https://www.irs.gov/pub/irs-prior/f4952--2025.pdf",
    ]
