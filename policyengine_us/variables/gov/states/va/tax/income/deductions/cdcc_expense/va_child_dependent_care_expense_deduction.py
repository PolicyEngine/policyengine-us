from policyengine_us.model_api import *


class va_child_dependent_care_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia child and dependent care expense deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2021-760-instructions.pdf#page=29"
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        # Virginia deducts the amount on which the federal credit is based
        # under IRC §21, which covers childcare plus care for a disabled
        # adult qualifying individual (care_expenses).
        childcare = tax_unit("tax_unit_childcare_expenses", period)
        adult_care = add(tax_unit, period, ["care_expenses"])
        expenses = childcare + adult_care
        cdcc_limit = tax_unit("va_child_dependent_care_deduction_cdcc_limit", period)
        eligible_capped_expenses = min_(expenses, cdcc_limit)
        # cap further to the lowest earnings between the taxpayer and spouse
        return min_(
            eligible_capped_expenses,
            tax_unit("min_head_spouse_earned", period),
        )
