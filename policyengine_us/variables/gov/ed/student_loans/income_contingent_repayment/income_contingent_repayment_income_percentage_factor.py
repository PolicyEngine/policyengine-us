from policyengine_us.model_api import *


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
        "the first row or above the last row takes that row's factor."
    )
    unit = "/1"
    definition_period = MONTH
    reference = (
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(f)(4)(i)(A)",
        "https://www.govinfo.gov/content/pkg/FR-2026-06-09/pdf/2026-11540.pdf#page=2",
        "https://www.govinfo.gov/content/pkg/FR-2026-06-09/pdf/2026-11540.pdf#page=4",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.ed.student_loans.income_contingent_repayment.income_percentage_factor
        agi = tax_unit(
            "income_driven_repayment_adjusted_gross_income", period.this_year
        )
        filing_status = tax_unit("filing_status", period.this_year)
        is_single = filing_status == filing_status.possible_values.SINGLE
        # The table rows are points to interpolate between, not brackets.
        single_factor = np.interp(agi, p.single.thresholds, p.single.amounts)
        married_factor = np.interp(
            agi,
            p.married_or_head_of_household.thresholds,
            p.married_or_head_of_household.amounts,
        )
        factor = where(is_single, single_factor, married_factor)
        # The notice rounds the interpolated factor to the nearest hundredth of
        # a percent, which is four decimal places of the fraction.
        return np.round(factor, 4)
