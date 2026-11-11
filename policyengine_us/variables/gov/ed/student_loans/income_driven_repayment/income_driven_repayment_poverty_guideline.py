from policyengine_us.model_api import *
from policyengine_us.variables.gov.ed.student_loans.student_loan_borrower_income_helpers import (
    poverty_guideline_for_family_size,
)


class income_driven_repayment_poverty_guideline(Variable):
    value_type = float
    entity = TaxUnit
    label = "Income-driven repayment poverty guideline"
    documentation = (
        "HHS poverty guideline for the tax unit's size. Alaska and Hawaii "
        "residents use their own guidelines; everyone else, including "
        "residents of the territories, uses the 48 contiguous states' "
        "guideline. Tax unit size stands in for the regulation's family size. "
        "This is the guideline for the head and spouse of the tax unit. A "
        "borrower claimed as a tax dependent uses the guideline for a family "
        "of one."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(b)(9)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(b)(14)",
    )

    def formula(tax_unit, period, parameters):
        size = tax_unit("tax_unit_size", period)
        return poverty_guideline_for_family_size(
            tax_unit.household, period, parameters, size
        )
