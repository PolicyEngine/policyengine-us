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
        expenses = tax_unit("tax_unit_childcare_expenses", period)
        cdcc_limit = tax_unit(
            "va_child_dependent_care_deduction_cdcc_limit", period
        )
        eligible_capped_expenses = min_(expenses, cdcc_limit)
        # cap further to the lowest earnings between the taxpayer and spouse
        return min_(
            eligible_capped_expenses,
            tax_unit("min_head_spouse_earned", period),
        )
