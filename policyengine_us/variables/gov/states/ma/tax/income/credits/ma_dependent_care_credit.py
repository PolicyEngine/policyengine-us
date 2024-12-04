from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.credits.cdcc.count_cdcc_eligible import (
    count_cdcc_eligible,
)


class ma_dependent_care_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.mass.gov/info-details/mass-general-laws-c62-ss-6"  # (y)
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ma.tax.income.credits.dependent_care
        # Expenses capped by number of qualifying individuals.
        expenses = tax_unit("tax_unit_childcare_expenses", period)
        count_cdcc_eligible = min_(
            tax_unit("count_cdcc_eligible", period), p.dependent_cap
        )
        # Line 1.
        capped_expenses = min_(expenses, p.amount * count_cdcc_eligible)
        # Skip lines 2 and 3, which are done in intermediate steps.
        # Line 4: Smallest of lines 1, 2, 3.
        amount_if_eligible = min_(
            capped_expenses, tax_unit("min_head_spouse_earned", period)
        )
        # Skip line 5 for prior-year expenses.
        # Married filing separate are ineligible.
        filing_status = tax_unit("filing_status", period)
        eligible = filing_status != filing_status.possible_values.SEPARATE
        return eligible * amount_if_eligible
