from policyengine_us.model_api import *
from policyengine_us.variables.gov.ed.student_loans.student_loan_borrower_income_helpers import (
    income_contingent_repayment_factor,
)


class income_contingent_repayment_income_percentage_factor(Variable):
    value_type = float
    entity = TaxUnit
    label = "Income-Contingent Repayment plan income percentage factor"
    documentation = (
        "Factor from the Department of Education's annual notice that scales "
        "the 12-year fixed payment under the Income-Contingent Repayment plan, "
        "based on adjusted gross income from the most recent return "
        "(income_driven_repayment_adjusted_gross_income). Single filers use "
        "the single table; "
        "joint, separate, head of household and surviving spouse filers use "
        "the married or head of household table. An income between two rows "
        "of the table is linearly interpolated and rounded to the nearest "
        "hundredth of a percent, as the notice instructs. An income below "
        "the first row or above the last row takes that row's factor. This is "
        "the factor for the head and spouse of the tax unit. A borrower "
        "claimed as a tax dependent takes the single table's factor at their "
        "own income."
    )
    unit = "/1"
    definition_period = MONTH
    reference = (
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(f)(4)(i)(A)",
        "https://www.govinfo.gov/content/pkg/FR-2026-06-09/pdf/2026-11540.pdf#page=2",
        "https://www.govinfo.gov/content/pkg/FR-2026-06-09/pdf/2026-11540.pdf#page=4",
    )

    def formula(tax_unit, period, parameters):
        agi = tax_unit(
            "income_driven_repayment_adjusted_gross_income", period.this_year
        )
        filing_status = tax_unit("filing_status", period.this_year)
        is_single = filing_status == filing_status.possible_values.SINGLE
        return income_contingent_repayment_factor(agi, is_single, period, parameters)
