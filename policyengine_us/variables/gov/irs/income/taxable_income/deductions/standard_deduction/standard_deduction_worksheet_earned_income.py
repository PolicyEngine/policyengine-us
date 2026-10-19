from policyengine_us.model_api import *


class standard_deduction_worksheet_earned_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Earned income for the standard deduction worksheet for dependents"
    unit = USD
    documentation = (
        "Earned income of the head and spouse on the Standard Deduction "
        "Worksheet for Dependents: wages from Form W-2 box 1, which leave out "
        "elective deferrals, plus business and farm income, minus the "
        "deductible part of self-employment tax, and not below zero."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/63#c_5",
        # Standard Deduction Worksheet for Dependents, Form 1040 instructions.
        "https://www.irs.gov/pub/irs-prior/i1040gi--2024.pdf#page=34",
        "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=35",
        # Publication 501, Table 8, line 1: "Enter your earned income (defined
        # below). If none, enter -0-."
        "https://www.irs.gov/pub/irs-prior/p501--2025.pdf#page=26",
    )

    def formula(tax_unit, period, parameters):
        # The head's and spouse's amounts: a dependent's earnings belong on
        # the dependent's own return. A joint return sums both spouses'
        # amounts before the zero floor.
        earned_income = tax_unit_non_dep_sum(
            "standard_deduction_worksheet_earned_income_person", tax_unit, period
        )
        return max_(earned_income, 0)
