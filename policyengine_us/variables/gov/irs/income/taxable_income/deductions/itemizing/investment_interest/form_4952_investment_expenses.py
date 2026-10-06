from policyengine_us.model_api import *


class form_4952_investment_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Form 4952 investment expenses"
    unit = USD
    definition_period = YEAR
    documentation = """
    Form 4952 line 5: "Investment expenses (see instructions)". Section
    163(d)(4)(C) includes "deductions allowed" other than interest that are
    "directly connected with the production of investment income", and the
    instructions include expenses "only if you are allowed a deduction on
    your return for the expense." The 2017 instructions require "the smaller
    of: (a) the investment expenses included on Schedule A (Form 1040), line
    23; or (b) the total on Schedule A (Form 1040), line 27." The model's
    misc_deduction applies the 2% AGI floor to the miscellaneous expense pool,
    which includes investment_expenses from Schedule A line 23. Only the
    head's and spouse's investment expenses count: a tax unit dependent's
    expenses belong on the dependent's own return.
    When misc.applies is false, these expenses are not allowed deductions
    and line 5 is zero. Section 67(h), as amended by P.L. 119-21 section
    70110, permanently disallows miscellaneous itemized deductions for
    taxable years beginning after December 31, 2017. No separate input
    identifies other allowed non-interest investment expenses.
    """
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/163#d_4_C",
        "https://www.law.cornell.edu/uscode/text/26/67#h",
        "https://www.irs.gov/pub/irs-prior/f4952--2017.pdf",
        "https://www.irs.gov/pub/irs-prior/f4952--2025.pdf#page=4",
    ]

    def formula(tax_unit, period, parameters):
        if not parameters(period).gov.irs.deductions.itemized.misc.applies:
            return 0
        expenses = tax_unit_non_dep_add(tax_unit, period, ["investment_expenses"])
        allowed_misc_deduction = tax_unit("misc_deduction", period)
        return min_(expenses, allowed_misc_deduction)
