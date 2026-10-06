from policyengine_us.model_api import *


class form_4952_total_investment_interest_expense(Variable):
    value_type = float
    entity = TaxUnit
    label = "Form 4952 total investment interest expense"
    unit = USD
    definition_period = YEAR
    documentation = """
    Form 4952 line 3: "Total investment interest expense. Add lines 1 and 2."
    Line 1 is "Investment interest expense paid or accrued in 2025": the head's
    and spouse's investment_interest_expense. A tax unit dependent's interest
    belongs on the dependent's own return, as irs_gross_income leaves out the
    dependent's income. Line 2 is the prior-year disallowed amount, which
    section 163(d)(2) carries forward as interest paid in this year.
    """
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/163#d_1",
        "https://www.law.cornell.edu/uscode/text/26/163#d_2",
        "https://www.law.cornell.edu/uscode/text/26/163#d_3",
        "https://www.irs.gov/pub/irs-prior/f4952--2025.pdf",
    ]

    def formula(tax_unit, period, parameters):
        # Line 1: interest paid or accrued this year by the head and spouse.
        paid = tax_unit_non_dep_add(tax_unit, period, ["investment_interest_expense"])
        # Line 2: interest disallowed last year.
        carryover = tax_unit(
            "form_4952_disallowed_investment_interest_expense_prior_year", period
        )
        return paid + carryover
