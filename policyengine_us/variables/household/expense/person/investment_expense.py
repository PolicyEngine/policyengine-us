from policyengine_us.model_api import *


class investment_expenses(Variable):
    value_type = float
    entity = Person
    label = "Non-interest expenses directly connected with investment income"
    documentation = """
    Expenses other than interest directly connected with producing
    investment income. Section 163(d)(4)(C) defines investment expenses
    as "deductions allowed under this chapter (other than for interest)
    which are directly connected with the production of investment income".
    Form 4952 line 5 includes only the allowed deduction for these expenses.
    Expenses taken into account in computing passive-activity income or
    loss under section 469 are excluded by section 163(d)(4)(D).
    """
    unit = USD
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/163#d_4_C",
        "https://www.law.cornell.edu/uscode/text/26/163#d_4_D",
        "https://www.irs.gov/pub/irs-prior/f4952--2025.pdf",
    ]
