from openfisca_us.model_api import *
from openfisca_us.variables.gov.irs.credits.cdcc.count_cdcc_eligible import (
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

    def formula(tax_unit, period, parameters):
        # Expenses capped by number of qualifying individuals.
        expenses = tax_unit("tax_unit_childcare_expenses", period)
        count_cdcc_eligible = tax_unit("count_cdcc_eligible", period)
        p = parameters(period).gov.states.ma.tax.income.credits.dependent_care
        cap = p.amount.calc(count_cdcc_eligible)
        # Line 1.
        capped_expenses = min_(expenses, cap)
        # Line 2: US Form 2441, line 4.
        person = tax_unit.members
        earned_income = max_(0, person("earned_income", period))
        is_joint = tax_unit("tax_unit_is_joint", period)
        is_spouse = person("is_tax_unit_spouse", period)
        is_head = person("is_tax_unit_head", period)
        head_earnings = tax_unit.sum(is_head * earned_income)
        # Line 3: US Form 2441, line 5 (for joint filers).
        spouse_earnings = tax_unit.sum(is_spouse * earned_income)
        # Form 2441: "all others, enter the amount from line 4"
        lower_earnings = where(
            is_joint, min_(head_earnings, spouse_earnings), head_earnings
        )
        # Line 4: Smallest of lines 1, 2, 3.
        amount_if_eligible = min_(capped_expenses, lower_earnings)
        # Skip line 5 for prior-year expenses.
        # Married filing separate are ineligible.
        filing_status = tax_unit("filing_status", period)
        eligible = filing_status != filing_status.possible_values.SEPARATE
        return eligible * amount_if_eligible
